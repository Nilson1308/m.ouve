"""Serviço reutilizável de notificações in-app para servidores."""

from __future__ import annotations

from django.contrib.auth import get_user_model

from atendimentos.models import NotificacaoInterna

User = get_user_model()


def criar_notificacao_interna(
    usuario_id,
    titulo: str,
    mensagem: str,
    *,
    link_acao: str | None = None,
) -> NotificacaoInterna | None:
    """
    Cria uma notificação interna para um servidor.

    Retorna None se o usuário não existir ou estiver inativo.
    """
    usuario = (
        User.objects.filter(pk=usuario_id, is_active=True)
        .only("id")
        .first()
    )
    if not usuario:
        return None
    return NotificacaoInterna.objects.create(
        usuario_destino_id=usuario_id,
        titulo=titulo[:255],
        mensagem=mensagem,
        link_acao=(link_acao or "")[:500],
    )