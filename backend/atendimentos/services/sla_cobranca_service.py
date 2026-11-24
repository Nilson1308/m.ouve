"""SLA, cobrança do cidadão, régua de escalonamento e digest por e-mail."""

from __future__ import annotations

import csv
import io
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from decouple import config
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count, Prefetch, Q, QuerySet
from django.template.loader import render_to_string
from django.utils import timezone

from atendimentos.backoffice_serializers import calcular_sla
from atendimentos.models import (
    CobrancaProtocolo,
    ConfiguracaoSlaCobranca,
    OrdemServico,
    Protocolo,
    ProtocoloHistorico,
    RelatorioSlaEnvio,
)
from atendimentos.services.escopo_dados import queryset_protocolos_escopo
from atendimentos.servicos_notificacao import criar_notificacao_interna
from catalogo.models import UnidadeAdministrativa
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

NIVEL_PREVENTIVO = "preventivo_80"
NIVEL_VENCIDO = "vencido"
NIVEL_ESCALONADO = "escalonado_controladoria"

RANK_NIVEL = {
    "": 0,
    NIVEL_PREVENTIVO: 1,
    NIVEL_VENCIDO: 2,
    NIVEL_ESCALONADO: 3,
}

CACHE_CIDRANCA_PREFIX = "cobranca_cidadao"


@dataclass
class ElegibilidadeCobranca:
    pode: bool
    motivo: str | None = None
    proxima_cobranca_em: datetime | None = None


def _config() -> ConfiguracaoSlaCobranca:
    return ConfiguracaoSlaCobranca.load()


def prazo_sla_dt(protocolo: Protocolo) -> datetime:
    if protocolo.prazo_sla:
        prazo = protocolo.prazo_sla
        return prazo if timezone.is_aware(prazo) else timezone.make_aware(prazo)
    sla = calcular_sla(protocolo)
    raw = sla.get("prazo_em")
    if not raw:
        horas = int(sla.get("sla_horas") or 72)
        return protocolo.data_criacao + timedelta(hours=horas)
    if isinstance(raw, datetime):
        return raw if timezone.is_aware(raw) else timezone.make_aware(raw)
    from django.utils.dateparse import parse_datetime

    parsed = parse_datetime(str(raw))
    if parsed is None:
        horas = int(sla.get("sla_horas") or 72)
        return protocolo.data_criacao + timedelta(hours=horas)
    return parsed if timezone.is_aware(parsed) else timezone.make_aware(parsed)


def sla_pausado(protocolo: Protocolo) -> bool:
    return bool(protocolo.sla_pausado_desde)


def sla_vencido(protocolo: Protocolo, agora: datetime | None = None) -> bool:
    agora = agora or timezone.now()
    if sla_pausado(protocolo):
        return False
    if protocolo.status == Protocolo.Status.AGUARDANDO_CIDADAO:
        return False
    return prazo_sla_dt(protocolo) < agora


def dias_atraso(protocolo: Protocolo, agora: datetime | None = None) -> int:
    agora = agora or timezone.now()
    prazo = prazo_sla_dt(protocolo)
    if agora <= prazo:
        return 0
    delta = agora - prazo
    return max(0, int(delta.total_seconds() // 86400))


def percentual_sla_consumido(protocolo: Protocolo, agora: datetime | None = None) -> float:
    agora = agora or timezone.now()
    prazo = prazo_sla_dt(protocolo)
    inicio = protocolo.data_criacao
    total = (prazo - inicio).total_seconds()
    if total <= 0:
        return 100.0
    elapsed = (agora - inicio).total_seconds()
    return min(100.0, max(0.0, 100.0 * elapsed / total))


def _cache_key_cobranca(protocolo_id) -> str:
    return f"{CACHE_CIDRANCA_PREFIX}:{protocolo_id}"


def proxima_cobranca_permitida(
    protocolo: Protocolo,
    cfg: ConfiguracaoSlaCobranca | None = None,
) -> datetime | None:
    cfg = cfg or _config()
    key = _cache_key_cobranca(protocolo.pk)
    if cache.get(key):
        ttl = cache.ttl(key) if hasattr(cache, "ttl") else None
        if ttl and ttl > 0:
            return timezone.now() + timedelta(seconds=int(ttl))
    if protocolo.ultima_cobranca_em:
        limite = protocolo.ultima_cobranca_em + timedelta(hours=int(cfg.cooldown_cobranca_horas))
        if limite > timezone.now():
            return limite
    return None


def avaliar_elegibilidade_cobranca(protocolo: Protocolo, usuario) -> ElegibilidadeCobranca:
    cfg = _config()
    if protocolo.usuario_id != usuario.pk:
        return ElegibilidadeCobranca(False, "nao_autorizado")
    if protocolo.status == Protocolo.Status.AGUARDANDO_CIDADAO or sla_pausado(protocolo):
        return ElegibilidadeCobranca(False, "aguardando_cidadao")
    if protocolo.status not in STATUS_ABERTOS:
        return ElegibilidadeCobranca(False, "encerrado")
    if not cfg.cobranca_cidadao_ativa:
        return ElegibilidadeCobranca(False, "desabilitado")
    if not sla_vencido(protocolo):
        return ElegibilidadeCobranca(False, "dentro_do_prazo")
    prox = proxima_cobranca_permitida(protocolo, cfg)
    if prox:
        return ElegibilidadeCobranca(False, "em_cooldown", prox)
    return ElegibilidadeCobranca(True)


def registrar_cooldown_cobranca(protocolo: Protocolo, cfg: ConfiguracaoSlaCobranca | None = None) -> None:
    cfg = cfg or _config()
    ttl = int(cfg.cooldown_cobranca_horas) * 3600
    cache.set(_cache_key_cobranca(protocolo.pk), "1", timeout=max(ttl, 60))


def _unidades_notificacao(protocolo: Protocolo) -> set[UUID]:
    ids: set[UUID] = set()
    if protocolo.servico_id and protocolo.servico.unidade_responsavel_id:
        ids.add(protocolo.servico.unidade_responsavel_id)
    for oid in (
        OrdemServico.objects.filter(protocolo_id=protocolo.pk)
        .exclude(status=OrdemServico.Status.CANCELADA)
        .values_list("unidade_id", flat=True)
    ):
        if oid:
            ids.add(oid)
    return ids


def notificar_cobranca_protocolo(protocolo: Protocolo, *, request=None) -> int:
    criadas = 0
    titulo = f"Cidadão cobrou retorno — {protocolo.codigo}"
    mensagem = (
        f"O cidadão registrou cobrança ({protocolo.qtd_cobrancas_cidadao}x) "
        f"sobre o protocolo {protocolo.codigo}, em atraso de SLA."
    )
    link = public_absolute_uri(request, f"/backoffice/protocolo/{protocolo.codigo}") or (
        f"/backoffice/protocolo/{protocolo.codigo}"
    )
    vistos: set = set()
    for uid in _unidades_notificacao(protocolo):
        for user_id in User.objects.filter(
            is_active=True, is_staff=True, unidade_id=uid
        ).values_list("pk", flat=True):
            if user_id in vistos:
                continue
            vistos.add(user_id)
            if criar_notificacao_interna(str(user_id), titulo, mensagem, link_acao=link):
                criadas += 1
    return criadas


def executar_cobranca_cidadao(
    protocolo: Protocolo,
    usuario,
    *,
    mensagem: str = "",
    request=None,
) -> CobrancaProtocolo:
    cfg = _config()
    eleg = avaliar_elegibilidade_cobranca(protocolo, usuario)
    if not eleg.pode:
        from rest_framework.exceptions import ValidationError, Throttled

        if eleg.motivo == "em_cooldown":
            raise Throttled(
                detail={
                    "detalhe": "Aguarde o intervalo entre cobranças.",
                    "proxima_cobranca_em": eleg.proxima_cobranca_em.strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    )
                    if eleg.proxima_cobranca_em
                    else None,
                }
            )
        raise ValidationError({"detalhe": _msg_bloqueio(eleg.motivo)})

    msg = (mensagem or "").strip()[:300]
    agora = timezone.now()
    cob = CobrancaProtocolo.objects.create(
        protocolo=protocolo,
        solicitante=usuario,
        mensagem=msg,
    )
    protocolo.qtd_cobrancas_cidadao = (protocolo.qtd_cobrancas_cidadao or 0) + 1
    protocolo.ultima_cobranca_em = agora
    protocolo.save(update_fields=["qtd_cobrancas_cidadao", "ultima_cobranca_em", "data_atualizacao"])
    ProtocoloHistorico.objects.create(
        protocolo=protocolo,
        status=protocolo.status,
        descricao=f"Cobrança do cidadão registrada ({protocolo.qtd_cobrancas_cidadao}ª).",
        equipe_nome="",
    )
    registrar_cooldown_cobranca(protocolo, cfg)
    notificar_cobranca_protocolo(protocolo, request=request)
    return cob


def _msg_bloqueio(motivo: str | None) -> str:
    mapa = {
        "dentro_do_prazo": "O protocolo ainda está dentro do prazo de atendimento.",
        "encerrado": "Protocolo encerrado — cobrança não permitida.",
        "desabilitado": "Cobrança pelo cidadão está desabilitada no momento.",
        "nao_autorizado": "Você não pode cobrar este protocolo.",
        "em_cooldown": "Aguarde o intervalo entre cobranças.",
    }
    return mapa.get(motivo or "", "Cobrança não permitida.")


def _link_protocolo_backoffice(codigo: str) -> str:
    base = config("BACKOFFICE_FRONTEND_BASE_URL", default="").strip().rstrip("/")
    if not base:
        base = config("PUBLIC_BASE_URL", default="").strip().rstrip("/")
    path = f"/backoffice/protocolo/{codigo}"
    return f"{base}{path}" if base else path


def _destinatarios_unidade(unidade_id) -> list[str]:
    emails = list(
        User.objects.filter(is_active=True, is_staff=True, unidade_id=unidade_id)
        .exclude(email="")
        .values_list("email", flat=True)
    )
    return [e.strip().lower() for e in emails if e and "@" in e]


def _destinatarios_controladoria(cfg: ConfiguracaoSlaCobranca) -> list[str]:
    raw = cfg.emails_controladoria if isinstance(cfg.emails_controladoria, list) else []
    out: list[str] = []
    for e in raw:
        if isinstance(e, str) and "@" in e:
            out.append(e.strip().lower())
    return list(dict.fromkeys(out))


def queryset_protocolos_atrasados(base: QuerySet | None = None) -> QuerySet:
    qs = base if base is not None else Protocolo.objects.all()
    qs = qs.filter(status__in=STATUS_ABERTOS).select_related(
        "servico",
        "servico__unidade_responsavel",
        "equipamento",
    )
    agora = timezone.now()
    ids: list[Any] = []
    for p in qs.iterator(chunk_size=200):
        if sla_vencido(p, agora):
            ids.append(p.pk)
    return Protocolo.objects.filter(pk__in=ids).select_related(
        "servico",
        "servico__unidade_responsavel",
        "equipamento",
    )


def _linha_protocolo_digest(protocolo: Protocolo, agora: datetime | None = None) -> dict[str, Any]:
    agora = agora or timezone.now()
    eq = protocolo.equipamento
    return {
        "codigo": protocolo.codigo,
        "servico": (protocolo.servico.nome if protocolo.servico_id else "—"),
        "equipamento": eq.nome if eq else "—",
        "dias_atraso": dias_atraso(protocolo, agora),
        "cobrancas": int(protocolo.qtd_cobrancas_cidadao or 0),
        "link": _link_protocolo_backoffice(protocolo.codigo),
        "unidade_id": str(protocolo.servico.unidade_responsavel_id)
        if protocolo.servico_id
        else None,
        "unidade_nome": protocolo.servico.unidade_responsavel.nome
        if protocolo.servico_id and protocolo.servico.unidade_responsavel_id
        else "—",
    }


def _enviar_email_digest(
    *,
    destinatarios: list[str],
    assunto: str,
    contexto: dict,
    cfg_tipo: str,
    unidade=None,
    disparado_por=None,
) -> RelatorioSlaEnvio:
    if not destinatarios:
        return RelatorioSlaEnvio.objects.create(
            tipo=cfg_tipo,
            unidade=unidade,
            destinatarios=[],
            total_protocolos=contexto.get("total_protocolos", 0),
            total_cobrados=contexto.get("total_cobrados", 0),
            status=RelatorioSlaEnvio.Status.SEM_PENDENCIAS,
            disparado_por=disparado_por,
        )
    html = render_to_string("atendimentos/email/sla_digest.html", contexto)
    text = render_to_string("atendimentos/email/sla_digest.txt", contexto)
    status = RelatorioSlaEnvio.Status.ENVIADO
    erro = ""
    try:
        msg = EmailMultiAlternatives(
            subject=assunto,
            body=text,
            to=destinatarios,
        )
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=False)
    except Exception as exc:
        logger.exception("Falha e-mail digest SLA: %s", exc)
        status = RelatorioSlaEnvio.Status.ERRO
        erro = str(exc)[:2000]
    return RelatorioSlaEnvio.objects.create(
        tipo=cfg_tipo,
        unidade=unidade,
        destinatarios=destinatarios,
        total_protocolos=contexto.get("total_protocolos", 0),
        total_cobrados=contexto.get("total_cobrados", 0),
        status=status,
        erro_detalhe=erro,
        disparado_por=disparado_por,
    )


def enviar_digest_sla_atrasados(
    *,
    unidade_id: UUID | None = None,
    incluir_controladoria: bool = True,
    disparado_por=None,
) -> list[RelatorioSlaEnvio]:
    cfg = _config()
    agora = timezone.now()
    qs = queryset_protocolos_atrasados()
    if unidade_id:
        qs = qs.filter(servico__unidade_responsavel_id=unidade_id)

    linhas = [_linha_protocolo_digest(p, agora) for p in qs]
    if not linhas:
        return [
            RelatorioSlaEnvio.objects.create(
                tipo=RelatorioSlaEnvio.Tipo.DIGEST_UNIDADE,
                destinatarios=[],
                total_protocolos=0,
                total_cobrados=0,
                status=RelatorioSlaEnvio.Status.SEM_PENDENCIAS,
                disparado_por=disparado_por,
            )
        ]

    por_unidade: dict[str, list[dict]] = {}
    for linha in linhas:
        uid = linha.get("unidade_id") or "sem_unidade"
        por_unidade.setdefault(uid, []).append(linha)

    envios: list[RelatorioSlaEnvio] = []
    for uid, grupo in por_unidade.items():
        unidade_obj = None
        if uid != "sem_unidade":
            unidade_obj = UnidadeAdministrativa.objects.filter(pk=uid).first()
        dest = _destinatarios_unidade(uid) if uid != "sem_unidade" else []
        total_cob = sum(int(g["cobrancas"]) for g in grupo)
        ctx = {
            "titulo": "Protocolos em atraso — resumo consolidado",
            "linhas": grupo,
            "total_protocolos": len(grupo),
            "total_cobrados": sum(1 for g in grupo if g["cobrancas"] > 0),
        }
        envios.append(
            _enviar_email_digest(
                destinatarios=dest,
                assunto=f"[M.Ouve] {len(grupo)} protocolo(s) em atraso — {grupo[0].get('unidade_nome', 'Unidade')}",
                contexto=ctx,
                cfg_tipo=RelatorioSlaEnvio.Tipo.DIGEST_UNIDADE
                if not disparado_por
                else RelatorioSlaEnvio.Tipo.DISPARO_MANUAL,
                unidade=unidade_obj,
                disparado_por=disparado_por,
            )
        )

    if incluir_controladoria:
        dest_ctrl = _destinatarios_controladoria(cfg)
        ranking: dict[str, dict] = {}
        for linha in linhas:
            nome = linha["unidade_nome"]
            bucket = ranking.setdefault(
                nome,
                {"unidade": nome, "total": 0, "cobrados": 0, "dias_max": 0},
            )
            bucket["total"] += 1
            if linha["cobrancas"] > 0:
                bucket["cobrados"] += 1
            bucket["dias_max"] = max(bucket["dias_max"], linha["dias_atraso"])
        ranking_list = sorted(ranking.values(), key=lambda x: (-x["total"], -x["cobrados"]))
        ctx_ctrl = {
            "titulo": "Controladoria — visão executiva de atrasos",
            "linhas": linhas,
            "ranking": ranking_list,
            "total_protocolos": len(linhas),
            "total_cobrados": sum(1 for g in linhas if g["cobrancas"] > 0),
        }
        envios.append(
            _enviar_email_digest(
                destinatarios=dest_ctrl,
                assunto=f"[M.Ouve] Resumo executivo — {len(linhas)} protocolo(s) vencidos",
                contexto=ctx_ctrl,
                cfg_tipo=RelatorioSlaEnvio.Tipo.DIGEST_CONTROLADORIA,
                disparado_por=disparado_por,
            )
        )
    return envios


def _deve_enviar_digest_agendado(cfg: ConfiguracaoSlaCobranca, agora: datetime) -> bool:
    if not cfg.digest_email_ativo:
        return False
    if agora.hour != int(cfg.digest_hora_envio):
        return False
    if cfg.digest_periodicidade == "semanal" and agora.weekday() != 0:
        return False
    cache_key = f"digest_sla:{agora.date().isoformat()}:h{cfg.digest_hora_envio}"
    if cache.get(cache_key):
        return False
    cache.set(cache_key, "1", timeout=86400)
    return True


def digest_agendado_se_aplica() -> bool:
    return _deve_enviar_digest_agendado(_config(), timezone.now())


def _notificar_escalonamento(protocolo: Protocolo, titulo: str, mensagem: str) -> int:
    criadas = 0
    link = _link_protocolo_backoffice(protocolo.codigo)
    vistos: set = set()
    for uid in _unidades_notificacao(protocolo):
        for user_id in User.objects.filter(
            is_active=True, is_staff=True, unidade_id=uid
        ).values_list("pk", flat=True):
            if user_id in vistos:
                continue
            vistos.add(user_id)
            if criar_notificacao_interna(str(user_id), titulo, mensagem, link_acao=link):
                criadas += 1
    return criadas


def _notificar_controladoria(cfg: ConfiguracaoSlaCobranca, protocolo: Protocolo) -> int:
    titulo = f"Escalonamento Controladoria — {protocolo.codigo}"
    mensagem = (
        f"Protocolo {protocolo.codigo} escalonado para Controladoria "
        f"({dias_atraso(protocolo)} dia(s) de atraso, "
        f"{protocolo.qtd_cobrancas_cidadao} cobrança(s) do cidadão)."
    )
    link = _link_protocolo_backoffice(protocolo.codigo)
    emails = set(_destinatarios_controladoria(cfg))
    criadas = 0
    for user in User.objects.filter(is_active=True, is_staff=True).exclude(email=""):
        mail = (user.email or "").strip().lower()
        if mail and mail in emails:
            if criar_notificacao_interna(str(user.pk), titulo, mensagem, link_acao=link):
                criadas += 1
    for admin in User.objects.filter(is_superuser=True, is_active=True):
        if criar_notificacao_interna(str(admin.pk), titulo, mensagem, link_acao=link):
            criadas += 1
    return criadas


def verificar_escalonamento_sla(*, limite: int = 500) -> int:
    cfg = _config()
    agora = timezone.now()
    qs = Protocolo.objects.filter(status__in=STATUS_ABERTOS).select_related("servico")[:limite]
    atualizados = 0
    for protocolo in qs:
        if sla_pausado(protocolo) or protocolo.status == Protocolo.Status.AGUARDANDO_CIDADAO:
            continue
        atual = (protocolo.ultimo_alerta_sla_nivel or "").strip()
        rank_atual = RANK_NIVEL.get(atual, 0)
        pct = percentual_sla_consumido(protocolo, agora)
        vencido = sla_vencido(protocolo, agora)
        dias = dias_atraso(protocolo, agora)
        novo_nivel = atual

        if (
            not vencido
            and pct >= int(cfg.alerta_preventivo_percentual)
            and rank_atual < RANK_NIVEL[NIVEL_PREVENTIVO]
        ):
            novo_nivel = NIVEL_PREVENTIVO
            _notificar_escalonamento(
                protocolo,
                f"SLA em {int(cfg.alerta_preventivo_percentual)}% — {protocolo.codigo}",
                f"O protocolo {protocolo.codigo} atingiu {int(pct)}% do prazo de SLA.",
            )
            ProtocoloHistorico.objects.create(
                protocolo=protocolo,
                status=protocolo.status,
                descricao=f"Alerta SLA: preventivo ({int(cfg.alerta_preventivo_percentual)}%).",
                equipe_nome="",
            )

        elif vencido and rank_atual < RANK_NIVEL[NIVEL_VENCIDO]:
            novo_nivel = NIVEL_VENCIDO
            _notificar_escalonamento(
                protocolo,
                f"SLA vencido — {protocolo.codigo}",
                f"O protocolo {protocolo.codigo} ultrapassou o prazo de atendimento.",
            )
            ProtocoloHistorico.objects.create(
                protocolo=protocolo,
                status=protocolo.status,
                descricao="Alerta SLA: prazo vencido.",
                equipe_nome="",
            )

        escala_ctrl = dias >= int(cfg.escalonamento_controladoria_dias) or (
            vencido and (protocolo.qtd_cobrancas_cidadao or 0) >= 1
        )
        if escala_ctrl and rank_atual < RANK_NIVEL[NIVEL_ESCALONADO]:
            novo_nivel = NIVEL_ESCALONADO
            _notificar_controladoria(cfg, protocolo)
            ProtocoloHistorico.objects.create(
                protocolo=protocolo,
                status=protocolo.status,
                descricao="Alerta SLA: escalonado à Controladoria.",
                equipe_nome="",
            )

        if novo_nivel != atual and RANK_NIVEL.get(novo_nivel, 0) > rank_atual:
            protocolo.ultimo_alerta_sla_nivel = novo_nivel
            protocolo.save(update_fields=["ultimo_alerta_sla_nivel", "data_atualizacao"])
            atualizados += 1
    return atualizados


def filtrar_relatorio_atrasados(
    user,
    *,
    unidade_id=None,
    servico_id=None,
    equipamento_id=None,
    apenas_cobrados: bool | None = None,
    dias_atraso_min: int | None = None,
    ordenacao: str = "atraso_desc",
) -> QuerySet:
    qs = queryset_protocolos_escopo(user, queryset_protocolos_atrasados())
    if unidade_id:
        qs = qs.filter(servico__unidade_responsavel_id=unidade_id)
    if servico_id:
        qs = qs.filter(servico_id=servico_id)
    if equipamento_id:
        qs = qs.filter(equipamento_id=equipamento_id)
    if apenas_cobrados:
        qs = qs.filter(qtd_cobrancas_cidadao__gte=1)

    agora = timezone.now()
    if dias_atraso_min is not None and dias_atraso_min > 0:
        ids = [p.pk for p in qs if dias_atraso(p, agora) >= dias_atraso_min]
        qs = qs.filter(pk__in=ids)

    if ordenacao == "cobrancas_desc":
        return qs.order_by("-qtd_cobrancas_cidadao", "-data_criacao")
    return qs.order_by("-data_criacao")


def resumo_relatorio_atrasados(qs: QuerySet) -> dict[str, Any]:
    agora = timezone.now()
    itens = list(qs.select_related("servico__unidade_responsavel", "equipamento"))
    total = len(itens)
    com_cobranca = sum(1 for p in itens if (p.qtd_cobrancas_cidadao or 0) >= 1)
    escalonados = sum(
        1
        for p in itens
        if (p.ultimo_alerta_sla_nivel or "") == NIVEL_ESCALONADO
    )
    por_unidade: dict[str, dict] = {}
    for p in itens:
        nome = (
            p.servico.unidade_responsavel.nome
            if p.servico_id and p.servico.unidade_responsavel_id
            else "—"
        )
        bucket = por_unidade.setdefault(
            nome,
            {"unidade_nome": nome, "total": 0, "com_cobranca": 0, "dias_max": 0},
        )
        bucket["total"] += 1
        if (p.qtd_cobrancas_cidadao or 0) >= 1:
            bucket["com_cobranca"] += 1
        bucket["dias_max"] = max(bucket["dias_max"], dias_atraso(p, agora))
    return {
        "total_atrasados": total,
        "total_com_cobranca": com_cobranca,
        "total_escalonados": escalonados,
        "por_unidade": sorted(por_unidade.values(), key=lambda x: -x["total"]),
    }


def serializar_item_relatorio(protocolo: Protocolo) -> dict[str, Any]:
    agora = timezone.now()
    prazo = prazo_sla_dt(protocolo)
    ordem = (
        OrdemServico.objects.filter(protocolo_id=protocolo.pk)
        .select_related("unidade", "despachado_por")
        .order_by("-criado_em")
        .first()
    )
    unidade_nome = "—"
    responsavel = "—"
    if ordem and ordem.unidade_id:
        unidade_nome = ordem.unidade.nome
        responsavel = (
            ordem.despachado_por.nome
            if ordem.despachado_por_id
            else (ordem.nome_equipe or ordem.unidade.nome)
        )
    elif protocolo.servico_id and protocolo.servico.unidade_responsavel_id:
        unidade_nome = protocolo.servico.unidade_responsavel.nome

    eq = protocolo.equipamento
    return {
        "protocolo_id": str(protocolo.pk),
        "codigo": protocolo.codigo,
        "servico_nome": protocolo.servico.nome if protocolo.servico_id else "—",
        "unidade_nome": unidade_nome,
        "equipamento": eq.nome if eq else None,
        "responsavel_nome": responsavel,
        "prazo_sla": prazo.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dias_atraso": dias_atraso(protocolo, agora),
        "qtd_cobrancas_cidadao": int(protocolo.qtd_cobrancas_cidadao or 0),
        "ultima_cobranca_em": protocolo.ultima_cobranca_em.strftime("%Y-%m-%dT%H:%M:%SZ")
        if protocolo.ultima_cobranca_em
        else None,
        "ultimo_alerta_sla_nivel": protocolo.ultimo_alerta_sla_nivel or "",
    }


def exportar_csv_relatorio_atrasados(qs: QuerySet) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        [
            "Protocolo",
            "Serviço",
            "Unidade",
            "Equipamento",
            "Responsável",
            "Prazo SLA",
            "Dias atraso",
            "Cobranças cidadão",
            "Última cobrança",
            "Último alerta SLA",
        ]
    )
    for protocolo in qs:
        item = serializar_item_relatorio(protocolo)
        writer.writerow(
            [
                item["codigo"],
                item["servico_nome"],
                item["unidade_nome"],
                item["equipamento"] or "",
                item["responsavel_nome"],
                item["prazo_sla"],
                item["dias_atraso"],
                item["qtd_cobrancas_cidadao"],
                item["ultima_cobranca_em"] or "",
                item["ultimo_alerta_sla_nivel"],
            ]
        )
    return buf.getvalue().encode("utf-8-sig")