"""Envio Web Push (pywebpush + VAPID)."""

from __future__ import annotations

import json
import logging
from typing import Any

from django.conf import settings

from atendimentos.models import NotificacaoCidadao, PushSubscription

logger = logging.getLogger(__name__)


def _vapid_claims() -> dict[str, str] | None:
    private = getattr(settings, "VAPID_PRIVATE_KEY", "") or ""
    email = getattr(settings, "VAPID_ADMIN_EMAIL", "") or ""
    if not private or not email:
        return None
    return {"sub": email, "privateKey": private}


def _deep_link_protocolo(notificacao: NotificacaoCidadao) -> str | None:
    if not notificacao.protocolo_id:
        return None
    codigo = getattr(notificacao.protocolo, "codigo", None)
    if not codigo:
        return None
    base = getattr(settings, "PWA_FRONTEND_BASE_URL", "") or ""
    path = f"/pwa/protocolos/{codigo}"
    if base:
        return f"{base.rstrip('/')}{path}"
    return path


def montar_payload_push(notificacao: NotificacaoCidadao) -> dict[str, Any]:
    url = _deep_link_protocolo(notificacao)
    data = {
        "notificacao_id": str(notificacao.id),
        "titulo": notificacao.titulo,
        "mensagem": notificacao.mensagem,
    }
    if notificacao.protocolo_id:
        data["protocolo_id"] = str(notificacao.protocolo_id)
        if getattr(notificacao.protocolo, "codigo", None):
            data["protocolo_codigo"] = notificacao.protocolo.codigo
    if url:
        data["url"] = url
    return {
        "title": notificacao.titulo,
        "body": notificacao.mensagem[:500],
        "data": data,
    }


def enviar_push_para_notificacao(notificacao_id: str) -> dict[str, int]:
    """
    Dispara Web Push para todas as inscrições do usuário.
    Retorna contadores {enviados, falhas, removidos}.
    """
    notif = (
        NotificacaoCidadao.objects.select_related("protocolo", "usuario")
        .filter(pk=notificacao_id)
        .first()
    )
    if not notif:
        logger.warning("NotificacaoCidadao inexistente: %s", notificacao_id)
        return {"enviados": 0, "falhas": 0, "removidos": 0}

    vapid = _vapid_claims()
    public_key = getattr(settings, "VAPID_PUBLIC_KEY", "") or ""
    if not vapid or not public_key:
        logger.info(
            "[WEB PUSH] VAPID não configurado; notificação %s persistida apenas in-app.",
            notificacao_id,
        )
        return {"enviados": 0, "falhas": 0, "removidos": 0, "ignorado": 1}

    from pywebpush import WebPushException, webpush

    payload = montar_payload_push(notif)
    payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    stats = {"enviados": 0, "falhas": 0, "removidos": 0}
    subs = list(PushSubscription.objects.filter(usuario_id=notif.usuario_id))

    for sub in subs:
        subscription_info = {
            "endpoint": sub.endpoint,
            "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
        }
        try:
            webpush(
                subscription_info=subscription_info,
                data=payload_bytes,
                vapid_private_key=vapid["privateKey"],
                vapid_claims={"sub": vapid["sub"]},
                timeout=10,
            )
            stats["enviados"] += 1
        except WebPushException as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            logger.warning(
                "Web Push falhou (status=%s) endpoint=%s: %s",
                status,
                sub.endpoint[:64],
                exc,
            )
            if status in (404, 410):
                sub.delete()
                stats["removidos"] += 1
            else:
                stats["falhas"] += 1
        except Exception as exc:
            logger.exception("Erro ao enviar Web Push: %s", exc)
            stats["falhas"] += 1

    return stats