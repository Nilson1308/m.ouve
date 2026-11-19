"""Notificações in-app e gatilhos de Web Push para o cidadão (PWA)."""

from __future__ import annotations

import logging

from django.db import transaction

from atendimentos.models import MensagemChat, NotificacaoCidadao, Protocolo, SessaoChat

logger = logging.getLogger(__name__)

STATUS_NOTIFICAVEIS = frozenset(
    {
        Protocolo.Status.EM_ANDAMENTO,
        Protocolo.Status.AGUARDANDO_REVISAO,
        Protocolo.Status.RESOLVIDO,
    }
)

TEMPLATES_STATUS: dict[str, tuple[str, str]] = {
    Protocolo.Status.EM_ANDAMENTO: (
        "Protocolo em andamento",
        "Sua solicitação {codigo} está sendo atendida pela equipe municipal.",
    ),
    Protocolo.Status.AGUARDANDO_REVISAO: (
        "Atualização no seu protocolo",
        (
            "O setor responsável concluiu o atendimento do protocolo {codigo}. "
            "Estamos finalizando a resposta oficial."
        ),
    ),
    Protocolo.Status.RESOLVIDO: (
        "Protocolo resolvido",
        (
            "Sua solicitação {codigo} foi respondida. "
            "Abra o aplicativo para ler a resposta e avaliar o atendimento."
        ),
    ),
}


def _preview_chat(texto: str, limite: int = 160) -> str:
    limpo = (texto or "").strip().replace("\n", " ")
    if len(limpo) <= limite:
        return limpo
    return limpo[: limite - 1] + "…"


@transaction.atomic
def criar_notificacao_cidadao(
    *,
    usuario,
    titulo: str,
    mensagem: str,
    protocolo: Protocolo | None = None,
    enfileirar_push: bool = True,
) -> NotificacaoCidadao:
    notif = NotificacaoCidadao.objects.create(
        usuario=usuario,
        protocolo=protocolo,
        titulo=titulo.strip()[:255],
        mensagem=mensagem.strip(),
    )
    if enfileirar_push:
        from atendimentos.tasks import enviar_notificacao_push_task

        transaction.on_commit(lambda: enviar_notificacao_push_task.delay(str(notif.id)))
    return notif


def notificar_status_protocolo(protocolo: Protocolo, status: str | None = None) -> NotificacaoCidadao | None:
    """Cria notificação quando o protocolo entra em status relevante para o cidadão."""
    status_atual = status or protocolo.status
    if status_atual not in STATUS_NOTIFICAVEIS:
        return None
    tpl = TEMPLATES_STATUS.get(status_atual)
    if not tpl:
        return None
    titulo, corpo_tpl = tpl
    mensagem = corpo_tpl.format(codigo=protocolo.codigo)
    return criar_notificacao_cidadao(
        usuario=protocolo.usuario,
        titulo=titulo,
        mensagem=mensagem,
        protocolo=protocolo,
    )


def notificar_resposta_ia_chat(sessao: SessaoChat, mensagem: MensagemChat) -> NotificacaoCidadao | None:
    """Avisa o cidadão sobre nova mensagem da assistente virtual."""
    if mensagem.autor != MensagemChat.Autor.IA:
        return None
    preview = _preview_chat(mensagem.conteudo_texto)
    if not preview:
        return None

    protocolo = None
    protocolo_id = sessao.protocolo_final_id
    if protocolo_id:
        protocolo = Protocolo.objects.filter(pk=protocolo_id).first()

    titulo = "Nova mensagem na conversa"
    if protocolo:
        titulo = f"Atualização — protocolo {protocolo.codigo}"
        mensagem_corpo = f"Assistente M.Ouve: {preview}"
    else:
        mensagem_corpo = f"Assistente M.Ouve: {preview}"

    return criar_notificacao_cidadao(
        usuario=sessao.usuario,
        titulo=titulo,
        mensagem=mensagem_corpo,
        protocolo=protocolo,
    )