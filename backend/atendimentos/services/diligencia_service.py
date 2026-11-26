"""Diligência com solicitante — pausa e retomada de SLA."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from uuid import UUID

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from atendimentos.models import (
    AnexoProtocolo,
    ConfiguracaoSlaCobranca,
    DiligenciaProtocolo,
    OrdemServico,
    Protocolo,
    ProtocoloHistorico,
)
from atendimentos.notificacoes_cidadao import criar_notificacao_cidadao
from atendimentos.servicos_notificacao import criar_notificacao_interna
from core_auth.rbac import usuario_e_super_admin, usuario_tem_permissao
from ouvia_core.url_utils import public_absolute_uri

logger = logging.getLogger(__name__)

PROTOCOLO_ENCERRADOS = frozenset(
    {
        Protocolo.Status.RESOLVIDO,
        Protocolo.Status.REJEITADO,
    }
)

OS_ABERTAS = frozenset(
    {
        OrdemServico.Status.PENDENTE,
        OrdemServico.Status.EM_ANDAMENTO,
        OrdemServico.Status.AGUARDANDO_CIDADAO,
        OrdemServico.Status.AGUARDANDO_FORMALIZACAO,
        OrdemServico.Status.AGUARDANDO_ASSINATURA,
    }
)


def _config() -> ConfiguracaoSlaCobranca:
    return ConfiguracaoSlaCobranca.load()


def sla_pausado(protocolo: Protocolo) -> bool:
    return bool(protocolo.sla_pausado_desde)


def _horas_sla_servico(protocolo: Protocolo) -> int:
    if protocolo.servico_id and protocolo.servico:
        return int(protocolo.servico.sla_horas or 72)
    return 72


def _materializar_prazo_protocolo(protocolo: Protocolo) -> None:
    if protocolo.prazo_sla:
        return
    protocolo.prazo_sla = protocolo.data_criacao + timedelta(
        hours=_horas_sla_servico(protocolo)
    )


def _materializar_prazo_ordem(ordem: OrdemServico) -> None:
    if ordem.prazo_sla or not ordem.prazo_horas:
        return
    ordem.prazo_sla = ordem.criado_em + timedelta(hours=int(ordem.prazo_horas))


def _congelar_sla_protocolo(protocolo: Protocolo, agora) -> None:
    _materializar_prazo_protocolo(protocolo)
    protocolo.sla_pausado_desde = agora


def _congelar_sla_ordem(ordem: OrdemServico, agora) -> None:
    _materializar_prazo_ordem(ordem)
    ordem.sla_pausado_desde = agora


@transaction.atomic
def _descongelar_sla(
    protocolo: Protocolo,
    *,
    ordem: OrdemServico | None = None,
    agora=None,
) -> None:
    agora = agora or timezone.now()
    if protocolo.sla_pausado_desde:
        delta = agora - protocolo.sla_pausado_desde
        _materializar_prazo_protocolo(protocolo)
        protocolo.prazo_sla = protocolo.prazo_sla + delta
        protocolo.tempo_sla_pausado_segundos += int(delta.total_seconds())
        protocolo.sla_pausado_desde = None

    status_restaurar = (protocolo.status_anterior_diligencia or "").strip()
    if status_restaurar:
        protocolo.status = status_restaurar
    protocolo.status_anterior_diligencia = ""
    protocolo.save(
        update_fields=[
            "prazo_sla",
            "sla_pausado_desde",
            "tempo_sla_pausado_segundos",
            "status",
            "status_anterior_diligencia",
            "data_atualizacao",
        ]
    )

    alvo_os = ordem
    if not alvo_os:
        alvo_os = (
            OrdemServico.objects.filter(
                protocolo_id=protocolo.pk,
                status=OrdemServico.Status.AGUARDANDO_CIDADAO,
            )
            .order_by("-criado_em")
            .first()
        )
    if alvo_os and alvo_os.sla_pausado_desde:
        delta = agora - alvo_os.sla_pausado_desde
        _materializar_prazo_ordem(alvo_os)
        if alvo_os.prazo_sla:
            alvo_os.prazo_sla = alvo_os.prazo_sla + delta
        alvo_os.tempo_sla_pausado_segundos += int(delta.total_seconds())
        alvo_os.sla_pausado_desde = None
        st_os = (alvo_os.status_anterior_diligencia or "").strip()
        if st_os:
            alvo_os.status = st_os
        alvo_os.status_anterior_diligencia = ""
        alvo_os.save(
            update_fields=[
                "prazo_sla",
                "sla_pausado_desde",
                "tempo_sla_pausado_segundos",
                "status",
                "status_anterior_diligencia",
                "atualizado_em",
            ]
        )


def diligencia_aguardando(protocolo: Protocolo) -> DiligenciaProtocolo | None:
    return (
        DiligenciaProtocolo.objects.filter(
            protocolo_id=protocolo.pk,
            status=DiligenciaProtocolo.Status.AGUARDANDO_CIDADAO,
        )
        .order_by("-criado_em")
        .first()
    )


def _contagem_diligencias(protocolo: Protocolo) -> int:
    return (
        DiligenciaProtocolo.objects.filter(protocolo_id=protocolo.pk)
        .exclude(status=DiligenciaProtocolo.Status.CANCELADA)
        .count()
    )


@dataclass
class ElegibilidadeAbrirDiligencia:
    pode: bool
    motivo: str | None = None


def avaliar_pode_abrir_diligencia(protocolo: Protocolo) -> ElegibilidadeAbrirDiligencia:
    cfg = _config()
    if not cfg.diligencia_ativa:
        return ElegibilidadeAbrirDiligencia(False, "desabilitado")
    if protocolo.status in PROTOCOLO_ENCERRADOS:
        return ElegibilidadeAbrirDiligencia(False, "protocolo_encerrado")
    if diligencia_aguardando(protocolo):
        return ElegibilidadeAbrirDiligencia(False, "diligencia_ativa")
    if _contagem_diligencias(protocolo) >= int(cfg.max_diligencias_por_protocolo):
        return ElegibilidadeAbrirDiligencia(False, "limite_diligencias")
    return ElegibilidadeAbrirDiligencia(True)


def avaliar_pode_abrir_diligencia_usuario(
    protocolo: Protocolo,
    user,
    *,
    ordem: OrdemServico | None = None,
) -> ElegibilidadeAbrirDiligencia:
    base = avaliar_pode_abrir_diligencia(protocolo)
    if not base.pode or not user:
        return base
    if usuario_e_super_admin(user) or usuario_tem_permissao(user, "mesa_trabalho", "criar"):
        return base
    if not usuario_tem_permissao(user, "painel_setorial", "criar"):
        return ElegibilidadeAbrirDiligencia(False, "sem_permissao")
    uid = getattr(user, "unidade_id", None)
    if not uid:
        return ElegibilidadeAbrirDiligencia(False, "sem_unidade")
    if ordem and ordem.unidade_id != uid:
        return ElegibilidadeAbrirDiligencia(False, "ordem_outra_unidade")
    return base


def estatisticas_diligencia_protocolo(protocolo: Protocolo) -> dict[str, Any]:
    respondidas = protocolo.diligencias.filter(
        status=DiligenciaProtocolo.Status.RESPONDIDA
    )
    qtd = respondidas.count()
    ultima = (
        respondidas.order_by("-respondida_em")
        .values_list("respondida_em", flat=True)
        .first()
    )
    qtd_anexos = 0
    for ids in respondidas.values_list("anexos_ids", flat=True):
        if ids:
            qtd_anexos += len(ids)
    return {
        "qtd_diligencias_respondidas": qtd,
        "ultima_diligencia_respondida_em": (
            ultima.strftime("%Y-%m-%dT%H:%M:%SZ") if ultima else None
        ),
        "qtd_anexos_diligencias": qtd_anexos,
    }


def _serializar_lista_diligencias(
    diligencias,
    protocolo: Protocolo,
    *,
    request=None,
) -> list[dict[str, Any]]:
    lista = list(diligencias)
    todos_ids: set[str] = set()
    for d in lista:
        todos_ids.update(str(x) for x in (d.anexos_ids or []))
    mapa = carregar_mapa_anexos_protocolo(protocolo.pk, todos_ids)
    return [
        serializar_diligencia_resumo(d, request=request, mapa_anexos=mapa) for d in lista
    ]


def _validar_anexos(protocolo: Protocolo, anexos_ids: list) -> list[str]:
    if not anexos_ids:
        return []
    ids: list[UUID] = []
    for raw in anexos_ids:
        try:
            ids.append(UUID(str(raw)))
        except (TypeError, ValueError) as exc:
            raise ValidationError("anexos_ids inválido.") from exc
    encontrados = set(
        AnexoProtocolo.objects.filter(protocolo_id=protocolo.pk, pk__in=ids).values_list(
            "pk", flat=True
        )
    )
    if len(encontrados) != len(ids):
        raise ValidationError("Um ou mais anexos não pertencem a este protocolo.")
    return [str(x) for x in ids]


def _notificar_cidadao_diligencia(diligencia: DiligenciaProtocolo) -> None:
    protocolo = diligencia.protocolo
    prazo = diligencia.prazo_resposta.strftime("%d/%m/%Y às %H:%M")
    criar_notificacao_cidadao(
        usuario=protocolo.usuario,
        titulo=f"Complementação necessária — {protocolo.codigo}",
        mensagem=(
            f"A municipalidade solicita informações adicionais sobre o protocolo "
            f"{protocolo.codigo}. Prazo para resposta: {prazo}.\n\n"
            f"{diligencia.pergunta}"
        ),
        protocolo=protocolo,
    )


def _notificar_unidade_resposta(diligencia: DiligenciaProtocolo, *, request=None) -> None:
    from ouvia_core.url_utils import public_absolute_uri

    protocolo = diligencia.protocolo
    link = public_absolute_uri(request, f"/backoffice/protocolo/{protocolo.pk}") or (
        f"/backoffice/protocolo/{protocolo.pk}"
    )
    titulo = f"Cidadão respondeu diligência — {protocolo.codigo}"
    mensagem = f"O protocolo {protocolo.codigo} recebeu resposta à solicitação de complementação."
    from django.contrib.auth import get_user_model

    User = get_user_model()
    for uid in User.objects.filter(
        is_active=True,
        is_staff=True,
        unidade_id=diligencia.unidade_solicitante_id,
    ).values_list("pk", flat=True):
        criar_notificacao_interna(str(uid), titulo, mensagem, link_acao=link)
    criar_notificacao_interna(
        str(diligencia.autor_servidor_id), titulo, mensagem, link_acao=link
    )


@transaction.atomic
def abrir_diligencia(
    protocolo: Protocolo,
    *,
    autor,
    unidade_solicitante_id,
    pergunta: str,
    exige_anexo: bool = False,
    ordem_servico_id=None,
    request=None,
) -> DiligenciaProtocolo:
    cfg = _config()
    eleg = avaliar_pode_abrir_diligencia(protocolo)
    if not eleg.pode:
        raise ValidationError({"detail": eleg.motivo or "Não é possível abrir diligência."})

    texto = (pergunta or "").strip()
    if not texto:
        raise ValidationError({"pergunta": "Informe a pergunta ou instrução ao cidadão."})

    protocolo = Protocolo.objects.select_for_update().select_related("servico", "usuario").get(
        pk=protocolo.pk
    )

    ordem = None
    if ordem_servico_id:
        ordem = OrdemServico.objects.select_for_update().get(
            pk=ordem_servico_id, protocolo_id=protocolo.pk
        )
        if ordem.status not in OS_ABERTAS:
            raise ValidationError({"ordem_servico_id": "Ordem não está aberta."})

    agora = timezone.now()
    prazo = agora + timedelta(days=int(cfg.prazo_diligencia_dias))

    protocolo.status_anterior_diligencia = protocolo.status
    protocolo.status = Protocolo.Status.AGUARDANDO_CIDADAO
    _congelar_sla_protocolo(protocolo, agora)
    protocolo.save(
        update_fields=[
            "status",
            "status_anterior_diligencia",
            "prazo_sla",
            "sla_pausado_desde",
            "data_atualizacao",
        ]
    )

    if ordem:
        ordem.status_anterior_diligencia = ordem.status
        ordem.status = OrdemServico.Status.AGUARDANDO_CIDADAO
        _congelar_sla_ordem(ordem, agora)
        ordem.save(
            update_fields=[
                "status",
                "status_anterior_diligencia",
                "prazo_sla",
                "sla_pausado_desde",
                "atualizado_em",
            ]
        )

    diligencia = DiligenciaProtocolo.objects.create(
        protocolo=protocolo,
        ordem_servico=ordem,
        unidade_solicitante_id=unidade_solicitante_id,
        autor_servidor=autor,
        pergunta=texto,
        exige_anexo=bool(exige_anexo),
        prazo_resposta=prazo,
    )

    ProtocoloHistorico.objects.create(
        protocolo=protocolo,
        status=protocolo.status,
        descricao=f"Diligência aberta: {texto[:500]}",
        equipe_nome="",
    )

    _notificar_cidadao_diligencia(diligencia)
    return diligencia


@transaction.atomic
def responder_diligencia(
    protocolo: Protocolo,
    diligencia_id,
    *,
    resposta: str,
    anexos_ids: list | None = None,
    request=None,
) -> DiligenciaProtocolo:
    diligencia = DiligenciaProtocolo.objects.select_for_update().get(
        pk=diligencia_id, protocolo_id=protocolo.pk
    )
    if diligencia.status != DiligenciaProtocolo.Status.AGUARDANDO_CIDADAO:
        raise ValidationError({"detail": "Diligência não está aguardando resposta."})

    texto = (resposta or "").strip()
    if not texto:
        raise ValidationError({"resposta": "A resposta não pode ser vazia."})

    anexos_norm = _validar_anexos(protocolo, anexos_ids or [])
    if diligencia.exige_anexo and not anexos_norm:
        raise ValidationError({"anexos_ids": "É obrigatório enviar ao menos um anexo."})

    agora = timezone.now()
    diligencia.resposta_cidadao = texto
    diligencia.anexos_ids = anexos_norm
    diligencia.status = DiligenciaProtocolo.Status.RESPONDIDA
    diligencia.respondida_em = agora
    diligencia.encerrada_em = agora
    diligencia.save()

    protocolo = Protocolo.objects.select_for_update().get(pk=protocolo.pk)
    _descongelar_sla(protocolo, ordem=diligencia.ordem_servico, agora=agora)

    ProtocoloHistorico.objects.create(
        protocolo=protocolo,
        status=protocolo.status,
        descricao="Cidadão respondeu à diligência de complementação.",
        equipe_nome="",
    )

    _notificar_unidade_resposta(diligencia, request=request)
    try:
        from atendimentos.services.agente_briefing_service import invalidar_cache_briefing_protocolo

        invalidar_cache_briefing_protocolo(protocolo)
    except Exception:
        pass
    return diligencia


@transaction.atomic
def cancelar_diligencia(
    diligencia_id,
    *,
    autor,
    motivo: str = "",
    request=None,
) -> DiligenciaProtocolo:
    diligencia = DiligenciaProtocolo.objects.select_for_update().get(pk=diligencia_id)
    if diligencia.status != DiligenciaProtocolo.Status.AGUARDANDO_CIDADAO:
        raise ValidationError({"detail": "Somente diligências aguardando podem ser canceladas."})

    agora = timezone.now()
    diligencia.status = DiligenciaProtocolo.Status.CANCELADA
    diligencia.encerrada_em = agora
    diligencia.save()

    protocolo = Protocolo.objects.select_for_update().get(pk=diligencia.protocolo_id)
    _descongelar_sla(protocolo, ordem=diligencia.ordem_servico, agora=agora)

    desc = "Diligência cancelada pelo servidor."
    if motivo.strip():
        desc += f" Motivo: {motivo.strip()[:400]}"
    ProtocoloHistorico.objects.create(
        protocolo=protocolo,
        status=protocolo.status,
        descricao=desc,
        equipe_nome="",
    )
    return diligencia


def _encerrar_protocolo_sem_resposta(protocolo: Protocolo, diligencia: DiligenciaProtocolo) -> None:
    protocolo.status = Protocolo.Status.REJEITADO
    protocolo.save(update_fields=["status", "data_atualizacao"])
    ProtocoloHistorico.objects.create(
        protocolo=protocolo,
        status=protocolo.status,
        descricao="Protocolo encerrado por falta de resposta à diligência.",
        equipe_nome="",
    )
    criar_notificacao_cidadao(
        usuario=protocolo.usuario,
        titulo=f"Protocolo encerrado — {protocolo.codigo}",
        mensagem=(
            f"O protocolo {protocolo.codigo} foi encerrado por falta de resposta "
            "à solicitação de complementação dentro do prazo."
        ),
        protocolo=protocolo,
    )


@transaction.atomic
def expirar_diligencia(diligencia: DiligenciaProtocolo) -> None:
    """Marca diligência expirada, descongela SLA e aplica política global."""
    diligencia = DiligenciaProtocolo.objects.select_for_update().get(pk=diligencia.pk)
    if diligencia.status != DiligenciaProtocolo.Status.AGUARDANDO_CIDADAO:
        return

    cfg = _config()
    agora = timezone.now()
    diligencia.status = DiligenciaProtocolo.Status.EXPIRADA
    diligencia.encerrada_em = agora
    diligencia.save()

    protocolo = Protocolo.objects.select_for_update().get(pk=diligencia.protocolo_id)

    if cfg.acao_expiracao_diligencia == "encerrar_sem_resposta":
        if protocolo.sla_pausado_desde:
            _descongelar_sla(protocolo, ordem=diligencia.ordem_servico, agora=agora)
        _encerrar_protocolo_sem_resposta(protocolo, diligencia)
    else:
        _descongelar_sla(protocolo, ordem=diligencia.ordem_servico, agora=agora)
        ProtocoloHistorico.objects.create(
            protocolo=protocolo,
            status=protocolo.status,
            descricao=(
                "Prazo da diligência expirado — protocolo devolvido à fila para decisão da unidade."
            ),
            equipe_nome="",
        )

    titulo = f"Diligência expirada — {protocolo.codigo}"
    mensagem = (
        f"O cidadão não respondeu à diligência do protocolo {protocolo.codigo} dentro do prazo."
    )
    from django.contrib.auth import get_user_model

    User = get_user_model()
    for uid in User.objects.filter(
        is_active=True,
        is_staff=True,
        unidade_id=diligencia.unidade_solicitante_id,
    ).values_list("pk", flat=True):
        criar_notificacao_interna(str(uid), titulo, mensagem)


def verificar_expiracao_diligencias(*, limite: int = 200) -> int:
    agora = timezone.now()
    qs = DiligenciaProtocolo.objects.filter(
        status=DiligenciaProtocolo.Status.AGUARDANDO_CIDADAO,
        prazo_resposta__lt=agora,
    ).order_by("prazo_resposta")[:limite]
    n = 0
    for d in qs:
        try:
            expirar_diligencia(d)
            n += 1
        except Exception:
            logger.exception("Falha ao expirar diligência %s", d.pk)
    return n


def serializar_anexo_protocolo(
    anexo: AnexoProtocolo,
    *,
    request=None,
) -> dict[str, Any]:
    """Formato canônico de anexo de protocolo (PWA / backoffice / diligência)."""
    mime = anexo.tipo_mime or "application/octet-stream"
    nome_arquivo = ""
    if anexo.arquivo and anexo.arquivo.name:
        nome_arquivo = anexo.arquivo.name.rsplit("/", 1)[-1]
    return {
        "id": str(anexo.id),
        "url": public_absolute_uri(
            request, anexo.arquivo.url if anexo.arquivo else None
        ),
        "nome_arquivo": nome_arquivo,
        "nome": nome_arquivo,
        "tipo": mime,
        "mime_type": mime,
        "criado_em": anexo.criado_em.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def carregar_mapa_anexos_protocolo(
    protocolo_id,
    anexos_ids: list[str] | set[str],
) -> dict[str, AnexoProtocolo]:
    if not anexos_ids:
        return {}
    uuids = []
    for raw in anexos_ids:
        try:
            uuids.append(UUID(str(raw)))
        except (TypeError, ValueError):
            continue
    if not uuids:
        return {}
    return {
        str(a.id): a
        for a in AnexoProtocolo.objects.filter(protocolo_id=protocolo_id, pk__in=uuids)
    }


def serializar_anexos_diligencia(
    anexos_ids: list | None,
    *,
    protocolo_id,
    request=None,
    mapa: dict[str, AnexoProtocolo] | None = None,
) -> list[dict[str, Any]]:
    ids = [str(x) for x in (anexos_ids or []) if x]
    if not ids:
        return []
    if mapa is None:
        mapa = carregar_mapa_anexos_protocolo(protocolo_id, ids)
    out: list[dict[str, Any]] = []
    for aid in ids:
        anexo = mapa.get(aid)
        if anexo:
            out.append(serializar_anexo_protocolo(anexo, request=request))
    return out


def serializar_diligencia_resumo(
    d: DiligenciaProtocolo,
    *,
    request=None,
    mapa_anexos: dict[str, AnexoProtocolo] | None = None,
) -> dict[str, Any]:
    protocolo_id = d.protocolo_id
    return {
        "id": str(d.id),
        "status": d.status,
        "pergunta": d.pergunta,
        "exige_anexo": d.exige_anexo,
        "prazo_resposta": d.prazo_resposta.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "resposta_cidadao": d.resposta_cidadao or "",
        "anexos_ids": d.anexos_ids or [],
        "anexos": serializar_anexos_diligencia(
            d.anexos_ids,
            protocolo_id=protocolo_id,
            request=request,
            mapa=mapa_anexos,
        ),
        "respondida_em": (
            d.respondida_em.strftime("%Y-%m-%dT%H:%M:%SZ") if d.respondida_em else None
        ),
        "criado_em": d.criado_em.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unidade_nome": d.unidade_solicitante.nome if d.unidade_solicitante_id else "",
    }


def serializar_diligencia_ativa_pwa(d: DiligenciaProtocolo | None) -> dict | None:
    if not d:
        return None
    return {
        "id": str(d.id),
        "pergunta": d.pergunta,
        "unidade_nome": d.unidade_solicitante.nome,
        "exige_anexo": d.exige_anexo,
        "prazo_resposta": d.prazo_resposta.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "criado_em": d.criado_em.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def campos_diligencia_backoffice(
    protocolo: Protocolo,
    *,
    request=None,
    user=None,
    ordem: OrdemServico | None = None,
) -> dict[str, Any]:
    ativa = diligencia_aguardando(protocolo)
    if user is not None:
        eleg = avaliar_pode_abrir_diligencia_usuario(protocolo, user, ordem=ordem)
    else:
        eleg = avaliar_pode_abrir_diligencia(protocolo)
    historico = _serializar_lista_diligencias(
        protocolo.diligencias.all().order_by("-criado_em")[:20],
        protocolo,
        request=request,
    )
    mapa = None
    if ativa and ativa.anexos_ids:
        mapa = carregar_mapa_anexos_protocolo(protocolo.pk, ativa.anexos_ids)
    return {
        "diligencia_ativa": (
            serializar_diligencia_resumo(ativa, request=request, mapa_anexos=mapa)
            if ativa
            else None
        ),
        "diligencias": historico,
        "sla_pausado": sla_pausado(protocolo),
        "tempo_sla_pausado_segundos": int(protocolo.tempo_sla_pausado_segundos or 0),
        "pode_abrir_diligencia": eleg.pode,
        "motivo_bloqueio_diligencia": eleg.motivo,
    }


def campos_diligencia_setorial_resumo(protocolo: Protocolo, ordem: OrdemServico) -> dict[str, Any]:
    stats = estatisticas_diligencia_protocolo(protocolo)
    aguardando = (
        protocolo.status == Protocolo.Status.AGUARDANDO_CIDADAO
        or ordem.status == OrdemServico.Status.AGUARDANDO_CIDADAO
    )
    sla_ordem = bool(ordem.sla_pausado_desde)
    return {
        **stats,
        "aguardando_cidadao": aguardando,
        "sla_pausado": sla_pausado(protocolo) or sla_ordem,
    }


def campos_diligencia_setorial_detalhe(
    ordem: OrdemServico,
    *,
    request=None,
    user=None,
) -> dict[str, Any]:
    protocolo = ordem.protocolo
    campos = campos_diligencia_backoffice(
        protocolo, request=request, user=user, ordem=ordem
    )
    campos.update(campos_diligencia_setorial_resumo(protocolo, ordem))
    return campos


def campos_diligencia_pwa(protocolo: Protocolo, *, request=None) -> dict[str, Any]:
    ativa = diligencia_aguardando(protocolo)
    qs = protocolo.diligencias.exclude(status=DiligenciaProtocolo.Status.CANCELADA).order_by(
        "-criado_em"
    )[:10]
    historico = _serializar_lista_diligencias(qs, protocolo, request=request)
    mapa = None
    if ativa and ativa.anexos_ids:
        mapa = carregar_mapa_anexos_protocolo(protocolo.pk, ativa.anexos_ids)
    ativa_payload = None
    if ativa:
        base = serializar_diligencia_ativa_pwa(ativa)
        base["anexos_ids"] = ativa.anexos_ids or []
        base["anexos"] = serializar_anexos_diligencia(
            ativa.anexos_ids,
            protocolo_id=protocolo.pk,
            request=request,
            mapa=mapa,
        )
        ativa_payload = base
    return {
        "aguardando_cidadao": protocolo.status == Protocolo.Status.AGUARDANDO_CIDADAO,
        "diligencia_ativa": ativa_payload,
        "diligencias": historico,
    }