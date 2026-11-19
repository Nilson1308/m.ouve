"""Envio de recuperação de senha (e-mail, SMS, WhatsApp) — adapters extensíveis."""

import logging
import re
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


def mascarar_email(email: str) -> str:
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    visivel = local[:2] if len(local) > 2 else local[:1]
    return f"{visivel}***@{domain}"


def mascarar_telefone(telefone: str) -> str:
    digits = re.sub(r"\D", "", telefone or "")
    if len(digits) < 4:
        return "(**) *****-****"
    return f"({digits[:2]}) *****-{digits[-4:]}"


class BaseRecoveryChannel(ABC):
    canal: str

    @abstractmethod
    def send(self, usuario, token_plano: str, link_redefinicao: str) -> bool:
        """Enfileira ou envia a mensagem de recuperação."""


class EmailRecoveryChannel(BaseRecoveryChannel):
    canal = "email"

    def send(self, usuario, token_plano: str, link_redefinicao: str) -> bool:
        # TODO: integrar SMTP, SendGrid, SES, etc.
        logger.info(
            "[recovery:email] destino=%s token_ref=%s link=%s",
            mascarar_email(usuario.email),
            token_plano[:8],
            link_redefinicao,
        )
        return True


class SmsRecoveryChannel(BaseRecoveryChannel):
    canal = "sms"

    def send(self, usuario, token_plano: str, link_redefinicao: str) -> bool:
        # TODO: integrar gateway SMS municipal
        logger.info(
            "[recovery:sms] destino=%s codigo_ref=%s",
            mascarar_telefone(usuario.telefone),
            token_plano[:8],
        )
        return True


class WhatsAppRecoveryChannel(BaseRecoveryChannel):
    canal = "whatsapp"

    def send(self, usuario, token_plano: str, link_redefinicao: str) -> bool:
        # TODO: integrar API WhatsApp Business / provedor Gov
        logger.info(
            "[recovery:whatsapp] destino=%s link=%s",
            mascarar_telefone(usuario.telefone),
            link_redefinicao,
        )
        return True


_CHANNELS = {
    "email": EmailRecoveryChannel(),
    "sms": SmsRecoveryChannel(),
    "whatsapp": WhatsAppRecoveryChannel(),
}


def enviar_recuperacao_senha(usuario, canal: str, token_plano: str, link_redefinicao: str) -> bool:
    adapter = _CHANNELS.get(canal)
    if not adapter:
        raise ValueError(f"Canal de recuperação não suportado: {canal}")
    return adapter.send(usuario, token_plano, link_redefinicao)
