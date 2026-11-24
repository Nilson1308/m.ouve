"""Janela de reabertura pós-conclusão e retrabalho (Sprint 4)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from atendimentos.models import (
    ConfiguracaoSlaCobranca,
    OrdemServico,
    Protocolo,
    ProtocoloHistorico,
    ReaberturaProtocolo,
)
from catalogo.models import ServicoCatalogo

User = get_user_model()

MOTIVOS_BLOQUEIO = frozenset(
    {
        "desabilitado",
        "nao_concluido",
        "janela_expirada",
        "limite_atingido",
        "encerrado_definitivamente",
    }
)


@dataclass(frozen=True)
class ElegibilidadeReabertura:
    pode: bool
    motivo: str | None
    reabertura_ate: object | None
    sugerir_reabertura_csat: bool
    prazo_efetivo_dias: int | None


def _config() -> ConfiguracaoSlaCobranca:
    return ConfiguracaoSlaCobranca.load()


def prazo_reabertura_efetivo_dias(servico: ServicoCatalogo, cfg: ConfiguracaoSlaCobranca | None = None) -> int | None:
    """
    Retorna dias da janela ou None se reabertura desabilitada (global ou override 0).
    """
    cfg = cfg or _config()
    if not cfg.reabertura_ativa:
        return None
    override = getattr(servico, "prazo_reabertura_dias", None)
    if override is not None:
        if int(override) == 0:
            return None
        return int(override)
    return int(cfg.prazo_reabertura_dias or 7)


def max_reaberturas_efetivo(cfg: ConfiguracaoSlaCobranca | None = None) -> int:
    cfg = cfg or _config()
    return max(1, int(cfg.max_reaberturas_por_protocolo or 1))


def _nota_csat_protocolo(protocolo: Protocolo) -> int | None:
    try:
        return protocolo.avaliacao.nota
    except Exception:
        if protocolo.nota_satisfacao:
            return int(protocolo.nota_satisfacao)
        return None


def _sugerir_csat(protocolo: Protocolo, cfg: ConfiguracaoSlaCobranca, pode: bool) -> bool:
    if not pode:
        return False
    nota = _nota_csat_protocolo(protocolo)
    if nota is None:
        return False
    return nota <= int(cfg.nota_csat_gatilho_reabertura or 2)


def avaliar_elegibilidade_reabertura(
    protocolo: Protocolo,
    *,
    agora=None,
    cfg: ConfiguracaoSlaCobranca | None = None,
) -> ElegibilidadeReabertura:
    agora = agora or timezone.now()
    cfg = cfg or _config()
    servico = protocolo.servico
    dias = prazo_reabertura_efetivo_dias(servico, cfg) if servico_id_ok(servico) else None

    if dias is None:
        return ElegibilidadeReabertura(
            False,
            "desabilitado",
            protocolo.reabertura_ate,
            False,
            None,
        )

    if protocolo.status != Protocolo.Status.RESOLVIDO:
        return ElegibilidadeReabertura(
            False,
            "nao_concluido",
            protocolo.reabertura_ate,
            False,
            dias,
        )

    if int(protocolo.qtd_reaberturas or 0) >= max_reaberturas_efetivo(cfg):
        return ElegibilidadeReabertura(
            False,
            "limite_atingido",
            protocolo.reabertura_ate,
            False,
            dias,
        )

    if protocolo.encerrado_definitivamente_em:
        return ElegibilidadeReabertura(
            False,
            "encerrado_definitivamente",
            protocolo.reabertura_ate,
            False,
            dias,
        )

    ate = protocolo.reabertura_ate
    if ate is None:
        return ElegibilidadeReabertura(
            False,
            "janela_expirada",
            None,
            False,
            dias,
        )
    if agora > ate:
        return ElegibilidadeReabertura(
            False,
            "janela_expirada",
            ate,
            False,
            dias,
        )

    pode = True
    return ElegibilidadeReabertura(
        pode,
        None,
        ate,
        _sugerir_csat(protocolo, cfg, pode),
        dias,
    )


def servico_id_ok(servico) -> bool:
    return servico is not None and servico.pk is not None


def mensagem_bloqueio_reabertura(motivo: str | None) -> str:
    mapa = {
        "desabilitado": "Reabertura não está habilitada para este serviço.",
        "nao_concluido": "Só é possível contestar protocolos já concluídos.",
        "janela_expirada": "O prazo para contestar este protocolo já expirou.",
        "limite_atingido": "Este protocolo já atingiu o limite de reaberturas permitidas.",
        "encerrado_definitivamente": "A janela de contestação foi encerrada definitivamente.",
    }
    return mapa.get(motivo or "", "Não é possível reabrir este protocolo.")


@transaction.atomic
def aplicar_janela_reabertura_apos_conclusao(protocolo: Protocolo, *, agora=None) -> None:
    """Chamado sempre que o protocolo transita para resolvido."""
    agora = agora or timezone.now()
    cfg = _config()
    protocolo = Protocolo.objects.select_for_update().get(pk=protocolo.pk)
    servico = ServicoCatalogo.objects.select_related("unidade_responsavel").get(
        pk=protocolo.servico_id
    )
    dias = prazo_reabertura_efetivo_dias(servico, cfg)
    update_fields = ["encerrado_definitivamente_em", "data_atualizacao"]

    protocolo.encerrado_definitivamente_em = None

    if (
        dias is not None
        and int(protocolo.qtd_reaberturas or 0) < max_reaberturas_efetivo(cfg)
    ):
        protocolo.reabertura_ate = agora + timedelta(days=dias)
        update_fields.append("reabertura_ate")
    else:
        protocolo.reabertura_ate = None
        update_fields.append("reabertura_ate")

    protocolo.save(update_fields=update_fields)


def _horas_sla_reabertura(protocolo: Protocolo, cfg: ConfiguracaoSlaCobranca) -> int:
    if cfg.prazo_sla_reabertura_dias:
        return int(cfg.prazo_sla_reabertura_dias) * 24
    if protocolo.servico_id and protocolo.servico:
        return int(protocolo.servico.sla_horas or 72)
    return 72


def _validar_anexos(protocolo: Protocolo, anexos_ids: list | None) -> list[str]:
    from atendimentos.services.diligencia_service import _validar_anexos as _v

    return _v(protocolo, anexos_ids or [])


def _recalcular_sla_pos_reabertura(
    protocolo: Protocolo, cfg: ConfiguracaoSlaCobranca, agora
) -> tuple[timezone.datetime | None, timezone.datetime]:
    anterior = protocolo.prazo_sla
    horas = _horas_sla_reabertura(protocolo, cfg)
    novo = agora + timedelta(hours=horas)
    protocolo.prazo_sla = novo
    protocolo.ultimo_alerta_sla_nivel = ""
    protocolo.sla_pausado_desde = None
    protocolo.tempo_sla_pausado_segundos = 0
    protocolo.status_anterior_diligencia = ""
    return anterior, novo


def _instrucao_retrabalho(protocolo: Protocolo, motivo: str) -> str:
    trecho = (motivo or "").strip()[:1500]
    return (
        f"Retrabalho por reabertura do cidadão no protocolo {protocolo.codigo}. "
        f"Motivo informado: {trecho}"
    )


def notificar_reabertura_ouvidoria(protocolo: Protocolo, *, request=None) -> int:
    from atendimentos.notificacoes_internas import _link
    from atendimentos.servicos_notificacao import criar_notificacao_interna

    titulo = f"Protocolo reaberto — {protocolo.codigo}"
    mensagem = (
        f"O cidadão contestou a conclusão do protocolo {protocolo.codigo}. "
        "O caso retornou para retrabalho."
    )
    link = _link(f"/backoffice/protocolo/{protocolo.codigo}", request)
    destinatarios = User.objects.filter(
        is_staff=True,
        is_active=True,
    ).filter(
        models.Q(unidade__isnull=True) | models.Q(perfil_acesso__codigo__in=("ouvidor", "super_admin"))
    )[
        :80
    ]
    criadas = 0
    for usuario in destinatarios:
        if criar_notificacao_interna(usuario.pk, titulo, mensagem, link_acao=link):
            criadas += 1
    return criadas


@transaction.atomic
def reabrir_protocolo(
    protocolo: Protocolo,
    solicitante,
    *,
    motivo: str,
    anexos_ids: list | None = None,
    request=None,
) -> ReaberturaProtocolo:
    motivo = (motivo or "").strip()
    if len(motivo) < 10:
        raise ValidationError({"motivo": "Informe pelo menos 10 caracteres no motivo."})

    protocolo = Protocolo.objects.select_for_update().get(pk=protocolo.pk)

    if protocolo.usuario_id != solicitante.pk:
        raise ValidationError({"detail": "Protocolo não encontrado."})

    eleg = avaliar_elegibilidade_reabertura(protocolo)
    if not eleg.pode:
        raise ValidationError({"detail": mensagem_bloqueio_reabertura(eleg.motivo)})

    anexos_norm = _validar_anexos(protocolo, anexos_ids)

    cfg = _config()
    agora = timezone.now()
    nota_csat = _nota_csat_protocolo(protocolo)
    prazo_anterior, novo_prazo = _recalcular_sla_pos_reabertura(protocolo, cfg, agora)

    servico = ServicoCatalogo.objects.select_related("unidade_responsavel").get(
        pk=protocolo.servico_id
    )
    ordem_criada = None
    status_destino = Protocolo.Status.EM_ANALISE

    if servico.fluxo_tramitacao == ServicoCatalogo.FluxoTramitacao.DIRETO_SECRETARIA:
        unidade = servico.unidade_responsavel
        if unidade and unidade.ativo:
            status_destino = Protocolo.Status.EM_ANDAMENTO
            prazo_h = servico.sla_horas or 72
            ordem_criada = OrdemServico.objects.create(
                protocolo=protocolo,
                unidade=unidade,
                descricao=_instrucao_retrabalho(protocolo, motivo),
                prazo_horas=prazo_h,
                nome_equipe=unidade.sigla or unidade.nome,
                status=OrdemServico.Status.PENDENTE,
                prazo_sla=agora + timedelta(hours=int(prazo_h)),
            )
            from atendimentos.notificacoes_internas import notificar_nova_os_unidade

            notificar_nova_os_unidade(ordem_criada, request=request)
            notificar_reabertura_ouvidoria(protocolo, request=request)
        else:
            status_destino = Protocolo.Status.EM_ANALISE
            notificar_reabertura_ouvidoria(protocolo, request=request)
    else:
        notificar_reabertura_ouvidoria(protocolo, request=request)

    protocolo.status = status_destino
    protocolo.qtd_reaberturas = int(protocolo.qtd_reaberturas or 0) + 1
    protocolo.ultima_reabertura_em = agora
    protocolo.reabertura_ate = None
    protocolo.encerrado_definitivamente_em = None
    protocolo.save(
        update_fields=[
            "status",
            "prazo_sla",
            "ultimo_alerta_sla_nivel",
            "sla_pausado_desde",
            "tempo_sla_pausado_segundos",
            "status_anterior_diligencia",
            "qtd_reaberturas",
            "ultima_reabertura_em",
            "reabertura_ate",
            "encerrado_definitivamente_em",
            "data_atualizacao",
        ]
    )

    reabertura = ReaberturaProtocolo.objects.create(
        protocolo=protocolo,
        solicitante=solicitante,
        motivo=motivo,
        anexos_ids=anexos_norm,
        nota_csat_origem=nota_csat,
        prazo_sla_anterior=prazo_anterior,
        novo_prazo_sla=novo_prazo,
        ordem_servico_criada=ordem_criada,
    )

    ProtocoloHistorico.objects.create(
        protocolo=protocolo,
        status=status_destino,
        descricao=(
            f"Protocolo reaberto pelo cidadão. Motivo: {motivo[:500]}"
            + (f" ({len(anexos_norm)} anexo(s))" if anexos_norm else "")
        ),
        equipe_nome="Cidadão",
    )

    from atendimentos.notificacoes_cidadao import notificar_status_protocolo

    notificar_status_protocolo(protocolo, status_destino)
    return reabertura


def encerrar_janelas_reabertura_expiradas(*, agora=None, limite: int = 500) -> int:
    agora = agora or timezone.now()
    qs = (
        Protocolo.objects.filter(
            status=Protocolo.Status.RESOLVIDO,
            reabertura_ate__lt=agora,
            encerrado_definitivamente_em__isnull=True,
        )
        .order_by("reabertura_ate")[:limite]
    )
    total = 0
    for protocolo in qs:
        protocolo.encerrado_definitivamente_em = agora
        protocolo.save(
            update_fields=["encerrado_definitivamente_em", "data_atualizacao"]
        )
        ProtocoloHistorico.objects.create(
            protocolo=protocolo,
            status=Protocolo.Status.RESOLVIDO,
            descricao="Janela de reabertura encerrada definitivamente.",
            equipe_nome="Sistema",
        )
        total += 1
    return total


def serializar_reabertura(
    r: ReaberturaProtocolo,
    *,
    request=None,
    mapa_anexos: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from atendimentos.services.diligencia_service import (
        carregar_mapa_anexos_protocolo,
        serializar_anexos_diligencia,
    )

    ids = r.anexos_ids or []
    if mapa_anexos is None and ids:
        mapa_anexos = carregar_mapa_anexos_protocolo(r.protocolo_id, ids)
    return {
        "id": str(r.id),
        "motivo": r.motivo,
        "anexos_ids": ids,
        "anexos": serializar_anexos_diligencia(
            ids,
            protocolo_id=r.protocolo_id,
            request=request,
            mapa=mapa_anexos,
        ),
        "nota_csat_origem": r.nota_csat_origem,
        "prazo_sla_anterior": (
            r.prazo_sla_anterior.strftime("%Y-%m-%dT%H:%M:%SZ")
            if r.prazo_sla_anterior
            else None
        ),
        "novo_prazo_sla": (
            r.novo_prazo_sla.strftime("%Y-%m-%dT%H:%M:%SZ") if r.novo_prazo_sla else None
        ),
        "ordem_servico_id": (
            str(r.ordem_servico_criada_id) if r.ordem_servico_criada_id else None
        ),
        "criado_em": r.criado_em.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def campos_reabertura_pwa(protocolo: Protocolo, *, request=None) -> dict[str, Any]:
    cfg = _config()
    eleg = avaliar_elegibilidade_reabertura(protocolo)
    reaberturas = list(protocolo.reaberturas.all().order_by("-criado_em")[:20])
    todos_ids: set[str] = set()
    for r in reaberturas:
        todos_ids.update(str(x) for x in (r.anexos_ids or []))
    mapa = {}
    if todos_ids:
        from atendimentos.services.diligencia_service import carregar_mapa_anexos_protocolo

        mapa = carregar_mapa_anexos_protocolo(protocolo.pk, todos_ids)
    return {
        "pode_reabrir": eleg.pode,
        "motivo_bloqueio_reabertura": eleg.motivo,
        "reabertura_ate": (
            eleg.reabertura_ate.strftime("%Y-%m-%dT%H:%M:%SZ")
            if eleg.reabertura_ate
            else None
        ),
        "qtd_reaberturas": int(protocolo.qtd_reaberturas or 0),
        "max_reaberturas_permitidas": max_reaberturas_efetivo(cfg),
        "sugerir_reabertura_csat": eleg.sugerir_reabertura_csat,
        "reaberturas": [
            serializar_reabertura(r, request=request, mapa_anexos=mapa)
            for r in reaberturas
        ],
    }


def campos_reabertura_backoffice(protocolo: Protocolo, *, request=None) -> dict[str, Any]:
    base = campos_reabertura_pwa(protocolo, request=request)
    base["reaberto"] = int(protocolo.qtd_reaberturas or 0) > 0
    base["ultima_reabertura_em"] = (
        protocolo.ultima_reabertura_em.strftime("%Y-%m-%dT%H:%M:%SZ")
        if protocolo.ultima_reabertura_em
        else None
    )
    return base


def cidadao_pode_anexar(protocolo: Protocolo) -> bool:
    """Upload de anexos pelo cidadão em protocolos não encerrados ou na janela de reabertura."""
    if protocolo.status == Protocolo.Status.REJEITADO:
        return False
    if protocolo.status != Protocolo.Status.RESOLVIDO:
        return True
    return avaliar_elegibilidade_reabertura(protocolo).pode