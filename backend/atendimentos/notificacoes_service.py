"""Simulação de envio de push (FCM / WebPush)."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def registrar_envio_push_simulado(
    *,
    usuario_id: str,
    titulo: str,
    corpo: str,
    dados_extras: dict[str, Any] | None = None,
) -> bool:
    extra = dados_extras or {}
    logger.info(
        "[PUSH SIMULADO] usuario=%s titulo=%r corpo=%r extras=%s",
        usuario_id,
        titulo,
        corpo,
        extra,
    )
    return True
