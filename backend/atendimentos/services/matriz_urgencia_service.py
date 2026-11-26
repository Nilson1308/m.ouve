"""Motor central da matriz de urgência (Sprint 4.6)."""

from __future__ import annotations

import logging
import unicodedata
from datetime import timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from atendimentos.models import (
    ConfiguracaoMatrizUrgencia,
    OrdemServico,
    Protocolo,
    ProtocoloHistorico,
    SuperOS,
)
from atendimentos.servicos_notificacao import criar_notificacao_interna
from atendimentos.services.diligencia_service import _materializar_prazo_protocolo
from atendimentos.services.escopo_dados import protocolo_no_escopo_usuario
from atendimentos.urgencia_constants import nivel_maior, normalizar_nivel, peso_nivel
from core_auth.rbac import usuario_pode_alterar_urgencia
from ouvia_core.url_utils import public_absolute_uri

User = get_user_model()
logger = logging.getLogger(__name__)

STATUS_ABERTOS = frozenset(
    {
        Protocolo.Status.EM_ANALISE,
        Protocolo.Status.EM_ANDAMENTO,
        Protocolo.Status.AGUARDANDO_REVISAO,
        Protocolo.Status.AGUARDANDO_CIDADAO,
    }
)


def _config() -> ConfiguracaoMatrizUrgencia:
    return ConfiguracaoMatrizUrgencia.load()


def _sem_acento(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def _texto_protocolo(protocolo: Protocolo) -> str:
    partes = [protocolo.descricao or ""]
    dados = protocolo.dados_dinamicos or {}
    for v in dados.values():
        if isinstance(v, str):
            partes.append(v)
    return _sem_acento(" ".join(partes))


def _valor_campo_normalizado(dados: dict, chave: str) -> str:
    if chave not in dados:
        return ""
    return _sem_acento(str(dados.get(chave) or ""))


def _registrar_historico(protocolo: Protocolo, descricao: str, *, equipe: str = "Matriz de urgência") -> None:
    ProtocoloHistorico.objects.create(
        protocolo=protocolo,
        status=protocolo.status,
        descricao=descricao[:4000],
        equipe_nome=equipe,
    )


def _aplicar_nivel(
    protocolo: Protocolo,
    nivel: str,
    *,
    origem: str,
    salvar: bool = True,
) -> str:
    nivel = normalizar_nivel(nivel)
    anterior = protocolo.urgencia
    protocolo.urgencia = nivel
    protocolo.urgencia_peso = peso_nivel(nivel)
    protocolo.urgencia_origem = origem
    if salvar:
        protocolo.save(
            update_fields=[
                "urgencia",
                "urgencia_peso",
                "urgencia_origem",
                "data_atualizacao",
            ]
        )
    return anterior


def _avaliar_regras_campo(protocolo: Protocolo, cfg: ConfiguracaoMatrizUrgencia) -> str | None:
    regras = cfg.regras_campo_urgencia or []
    if not isinstance(regras, list):
        return None
    dados = protocolo.dados_dinamicos or {}
    melhor = None
    peso = peso_nivel(protocolo.urgencia)
    for regra in regras:
        if not isinstance(regra, dict):
            continue
        chave = (regra.get("chave_schema") or "").strip()
        valor_esperado = _sem_acento(str(regra.get("valor") or ""))
        nivel = normalizar_nivel(regra.get("urgencia"))
        if not chave or not valor_esperado:
            continue
        atual = _valor_campo_normalizado(dados, chave)
        if atual == valor_esperado or valor_esperado in atual:
            if peso_nivel(nivel) > peso:
                melhor = nivel
                peso = peso_nivel(nivel)
    return melhor


def _avaliar_ia(protocolo: Protocolo, cfg: ConfiguracaoMatrizUrgencia) -> tuple[str | None, float, str]:
    """Heurística configurável (sem vocabulário fixo de município no código)."""
    if not cfg.ia_urgencia_ativa:
        return None, 0.0, ""
    criterios = cfg.criterios_ia_customizados or {}
    if not isinstance(criterios, dict):
        return None, 0.0, ""
    texto = _texto_protocolo(protocolo)
    melhor_nivel = None
    melhor_score = 0
    motivos: list[str] = []
    for nivel_chave in ("critica", "alta"):
        bloco = criterios.get(nivel_chave) or {}
        sinais = bloco.get("sinais") or bloco.get("criterios") or []
        if isinstance(sinais, str):
            sinais = [sinais]
        if not isinstance(sinais, list):
            continue
        hits = 0
        for sinal in sinais:
            termo = _sem_acento(str(sinal or "").strip())
            if len(termo) < 3:
                continue
            if termo in texto:
                hits += 1
                motivos.append(termo)
        if hits > melhor_score:
            melhor_score = hits
            melhor_nivel = nivel_chave
    if not melhor_nivel or melhor_score == 0:
        return None, 0.0, ""
    confianca = min(0.99, 0.55 + 0.12 * melhor_score)
    return melhor_nivel, confianca, "; ".join(motivos[:8])


def aplicar_impacto_sla_urgencia(protocolo: Protocolo, cfg: ConfiguracaoMatrizUrgencia | None = None) -> bool:
    cfg = cfg or _config()
    if not cfg.urgencia_reduz_sla:
        return False
    nivel = normalizar_nivel(protocolo.urgencia)
    if nivel not in ("alta", "critica"):
        return False
    if protocolo.sla_pausado_desde:
        return False
    horas_base = int(protocolo.servico.sla_horas or 72) if protocolo.servico_id else 72
    _materializar_prazo_protocolo(protocolo)
    if not protocolo.prazo_sla:
        protocolo.prazo_sla = protocolo.data_criacao + timedelta(hours=horas_base)
    original = protocolo.data_criacao + timedelta(hours=horas_base)
    fator = (
        cfg.fator_sla_critica_percentual
        if nivel == "critica"
        else cfg.fator_sla_alta_percentual
    )
    fator = max(5, min(95, int(fator)))
    novo_delta = timedelta(hours=max(horas_base * fator / 100, 1))
    candidato = protocolo.data_criacao + novo_delta
    if nivel == "critica":
        piso = timezone.now() + timedelta(hours=max(1, int(cfg.sla_minimo_critica_horas)))
        if candidato < piso:
            candidato = piso
    if protocolo.prazo_sla and candidato >= protocolo.prazo_sla:
        return False
    protocolo.prazo_sla = candidato
    protocolo.save(update_fields=["prazo_sla", "data_atualizacao"])
    OrdemServico.objects.filter(
        protocolo_id=protocolo.pk,
        status__in=[
            OrdemServico.Status.PENDENTE,
            OrdemServico.Status.EM_ANDAMENTO,
            OrdemServico.Status.AGUARDANDO_CIDADAO,
            OrdemServico.Status.AGUARDANDO_FORMALIZACAO,
        ],
    ).update(prazo_sla=candidato)
    _registrar_historico(
        protocolo,
        f"SLA recalculado por urgência {nivel} "
        f"(referência original ~{original.isoformat()}, novo prazo {candidato.isoformat()}).",
    )
    return True


def disparar_alertas_urgencia(
    protocolo: Protocolo,
    nivel_anterior: str | None,
    *,
    cfg: ConfiguracaoMatrizUrgencia | None = None,
    request=None,
) -> int:
    cfg = cfg or _config()
    nivel = normalizar_nivel(protocolo.urgencia)
    ant = normalizar_nivel(nivel_anterior)
    if peso_nivel(nivel) <= peso_nivel(ant):
        return 0
    link = public_absolute_uri(request, f"/backoffice/protocolo/{protocolo.codigo}") or (
        f"/backoffice/protocolo/{protocolo.codigo}"
    )
    criadas = 0
    unidade_ids: set = set()
    for os in protocolo.ordens_servico.all():
        if os.unidade_id:
            unidade_ids.add(os.unidade_id)
    if protocolo.servico_id and protocolo.servico.unidade_responsavel_id:
        unidade_ids.add(protocolo.servico.unidade_responsavel_id)

    if nivel == "alta" and cfg.notificar_gestor_em_alta:
        qs = User.objects.filter(is_active=True, is_staff=True, unidade_id__in=unidade_ids)
        titulo = f"Urgência ALTA — {protocolo.codigo}"
        msg = f"Protocolo {protocolo.codigo} classificado com urgência alta."
        for u in qs:
            if criar_notificacao_interna(u.pk, titulo, msg, link_acao=link):
                criadas += 1

    if nivel == "critica" and cfg.notificar_controladoria_em_critica:
        titulo = f"Urgência CRÍTICA — {protocolo.codigo}"
        msg = f"Protocolo {protocolo.codigo} em nível crítico — ação imediata."
        dest = User.objects.filter(
            is_active=True,
            is_staff=True,
            perfil_acesso__codigo__in=["ouvidor", "super_admin", "controladoria"],
        )
        for u in dest:
            if criar_notificacao_interna(u.pk, titulo, msg, link_acao=link):
                criadas += 1
        for u in User.objects.filter(is_active=True, is_staff=True, unidade_id__in=unidade_ids):
            if criar_notificacao_interna(u.pk, titulo, msg, link_acao=link):
                criadas += 1
    return criadas


@transaction.atomic
def classificar_urgencia_entrada(protocolo: Protocolo) -> Protocolo:
    cfg = _config()
    if not cfg.matriz_ativa:
        return protocolo
    protocolo = Protocolo.objects.select_for_update().get(pk=protocolo.pk)
    servico = protocolo.servico
    nivel = normalizar_nivel(getattr(servico, "urgencia_padrao", None) if servico else None)
    _aplicar_nivel(protocolo, nivel, origem=Protocolo.UrgenciaOrigem.CATALOGO, salvar=False)

    regra = _avaliar_regras_campo(protocolo, cfg)
    if regra:
        _aplicar_nivel(protocolo, regra, origem=Protocolo.UrgenciaOrigem.REGRA, salvar=False)

    sugerida, conf, motivo = _avaliar_ia(protocolo, cfg)
    protocolo.urgencia_sugerida_ia = sugerida or ""
    protocolo.urgencia_motivo_ia = motivo or ""
    protocolo.urgencia_confianca_ia = conf if sugerida else None

    if sugerida and peso_nivel(sugerida) > peso_nivel(protocolo.urgencia):
        if cfg.ia_urgencia_modo == "aplicar_automatico" and conf >= float(cfg.ia_confianca_minima):
            anterior = _aplicar_nivel(protocolo, sugerida, origem=Protocolo.UrgenciaOrigem.IA, salvar=False)
            protocolo.urgencia_sugestao_status = Protocolo.UrgenciaSugestaoStatus.ACEITA
            _registrar_historico(
                protocolo,
                f"Urgência elevada para {sugerida} (IA, confiança {conf:.2f}). {motivo}",
            )
            aplicar_impacto_sla_urgencia(protocolo, cfg)
            disparar_alertas_urgencia(protocolo, anterior, cfg=cfg)
        else:
            protocolo.urgencia_sugestao_status = Protocolo.UrgenciaSugestaoStatus.PENDENTE

    protocolo.save(
        update_fields=[
            "urgencia",
            "urgencia_peso",
            "urgencia_origem",
            "urgencia_sugerida_ia",
            "urgencia_motivo_ia",
            "urgencia_confianca_ia",
            "urgencia_sugestao_status",
            "data_atualizacao",
        ]
    )
    if protocolo.urgencia == Protocolo.Urgencia.CRITICA:
        from atendimentos.services.agente_briefing_service import (
            invalidar_cache_ao_protocolo_critico,
        )

        invalidar_cache_ao_protocolo_critico(protocolo)
    return protocolo


@transaction.atomic
def avaliar_escalonamento_super_os(super_os: SuperOS) -> int:
    cfg = _config()
    if not cfg.matriz_ativa or not cfg.super_os_escalonamento_ativo:
        return 0
    qtd = super_os.protocolos_filhos.filter(
        status__in=STATUS_ABERTOS,
    ).count()
    nivel_alvo = None
    if qtd >= int(cfg.super_os_limite_critica):
        nivel_alvo = "critica"
    elif qtd >= int(cfg.super_os_limite_alta):
        nivel_alvo = "alta"
    if not nivel_alvo:
        return 0
    atualizados = 0
    filhos = list(
        super_os.protocolos_filhos.select_for_update().filter(status__in=STATUS_ABERTOS)
    )
    for protocolo in filhos:
        if protocolo.urgencia_travada_manualmente:
            continue
        if peso_nivel(nivel_alvo) <= peso_nivel(protocolo.urgencia):
            continue
        anterior = _aplicar_nivel(
            protocolo, nivel_alvo, origem=Protocolo.UrgenciaOrigem.SUPER_OS, salvar=True
        )
        _registrar_historico(
            protocolo,
            f"Escalonamento Super OS {super_os.codigo} ({qtd} protocolos): urgência → {nivel_alvo}.",
        )
        aplicar_impacto_sla_urgencia(protocolo, cfg)
        disparar_alertas_urgencia(protocolo, anterior, cfg=cfg)
        atualizados += 1
    return atualizados


@transaction.atomic
def alterar_urgencia_protocolo(
    protocolo: Protocolo,
    *,
    user,
    urgencia: str | None = None,
    acao: str | None = None,
    justificativa: str = "",
) -> Protocolo:
    if not usuario_pode_alterar_urgencia(user):
        raise PermissionDenied("Sem permissão para alterar urgência do protocolo.")
    if not protocolo_no_escopo_usuario(user, protocolo):
        raise PermissionDenied("Protocolo fora do escopo deste usuário.")

    protocolo = Protocolo.objects.select_for_update().get(pk=protocolo.pk)
    cfg = _config()
    acao_norm = (acao or "").strip().lower()

    if acao_norm == "aceitar_sugestao_ia":
        if protocolo.urgencia_sugestao_status != Protocolo.UrgenciaSugestaoStatus.PENDENTE:
            raise ValidationError({"detail": "Não há sugestão de IA pendente."})
        sugerida = normalizar_nivel(protocolo.urgencia_sugerida_ia)
        if not sugerida:
            raise ValidationError({"detail": "Sugestão de IA inválida."})
        anterior = _aplicar_nivel(protocolo, sugerida, origem=Protocolo.UrgenciaOrigem.IA, salvar=False)
        protocolo.urgencia_sugestao_status = Protocolo.UrgenciaSugestaoStatus.ACEITA
        protocolo.urgencia_travada_manualmente = True
        protocolo.save(
            update_fields=[
                "urgencia",
                "urgencia_peso",
                "urgencia_origem",
                "urgencia_sugestao_status",
                "urgencia_travada_manualmente",
                "data_atualizacao",
            ]
        )
        msg = (justificativa or "Sugestão de IA aceita.").strip()
        _registrar_historico(protocolo, f"{msg} Urgência: {anterior} → {sugerida}.")
        aplicar_impacto_sla_urgencia(protocolo, cfg)
        disparar_alertas_urgencia(protocolo, anterior, cfg=cfg)
        return protocolo

    if acao_norm == "descartar_sugestao_ia":
        if protocolo.urgencia_sugestao_status != Protocolo.UrgenciaSugestaoStatus.PENDENTE:
            raise ValidationError({"detail": "Não há sugestão de IA pendente."})
        protocolo.urgencia_sugestao_status = Protocolo.UrgenciaSugestaoStatus.DESCARTADA
        protocolo.save(update_fields=["urgencia_sugestao_status", "data_atualizacao"])
        _registrar_historico(protocolo, (justificativa or "Sugestão de urgência da IA descartada.").strip())
        return protocolo

    if not urgencia:
        raise ValidationError({"urgencia": "Informe o nível ou uma ação de sugestão IA."})
    just = (justificativa or "").strip()
    if len(just) < 10:
        raise ValidationError(
            {"justificativa": "Justificativa obrigatória com no mínimo 10 caracteres."}
        )
    novo = normalizar_nivel(urgencia)
    anterior = _aplicar_nivel(protocolo, novo, origem=Protocolo.UrgenciaOrigem.MANUAL, salvar=False)
    protocolo.urgencia_travada_manualmente = True
    protocolo.urgencia_sugestao_status = ""
    protocolo.save(
        update_fields=[
            "urgencia",
            "urgencia_peso",
            "urgencia_origem",
            "urgencia_travada_manualmente",
            "urgencia_sugestao_status",
            "data_atualizacao",
        ]
    )
    _registrar_historico(
        protocolo,
        f"Alteração manual de urgência ({anterior} → {novo}). Justificativa: {just}",
        equipe=user.nome if getattr(user, "nome", None) else "Backoffice",
    )
    aplicar_impacto_sla_urgencia(protocolo, cfg)
    disparar_alertas_urgencia(protocolo, anterior, cfg=cfg)
    return protocolo