"""Disparo em massa de notificações internas (broadcast)."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import transaction

from atendimentos.servicos_notificacao import criar_notificacao_interna
from catalogo.models import UnidadeAdministrativa

User = get_user_model()


def _prefixar_titulo_urgencia(titulo: str, nivel_urgencia: str) -> str:
    titulo = (titulo or "").strip()
    if nivel_urgencia == "alta":
        prefixo = "[Urgência alta] "
        if not titulo.startswith(prefixo):
            return f"{prefixo}{titulo}"[:255]
    return titulo[:255]


def _destinatarios_broadcast(unidade_alvo_id=None):
    qs = User.objects.filter(is_active=True, is_staff=True).only("id")
    if unidade_alvo_id:
        qs = qs.filter(unidade_id=unidade_alvo_id)
    return qs


@transaction.atomic
def executar_broadcast_notificacoes(
    *,
    titulo: str,
    mensagem: str,
    unidade_alvo_id=None,
    nivel_urgencia: str = "normal",
    link_acao: str = "",
) -> dict:
    """
    Cria uma notificação interna por destinatário elegível (staff ativo).

    Se ``unidade_alvo_id`` for informado, restringe à unidade; caso contrário, global.
    """
    if unidade_alvo_id:
        if not UnidadeAdministrativa.objects.filter(
            pk=unidade_alvo_id, ativo=True
        ).exists():
            raise ValueError("Unidade alvo inexistente ou inativa.")

    titulo_final = _prefixar_titulo_urgencia(titulo, nivel_urgencia)
    corpo = (mensagem or "").strip()
    if nivel_urgencia == "alta" and corpo and not corpo.endswith("."):
        corpo = f"{corpo}\n\nPrioridade: alta."

    destinatarios = list(_destinatarios_broadcast(unidade_alvo_id))
    criadas = 0
    for usuario in destinatarios:
        if criar_notificacao_interna(
            usuario.pk,
            titulo_final,
            corpo,
            link_acao=link_acao or None,
        ):
            criadas += 1

    return {
        "criadas": criadas,
        "destinatarios_elegiveis": len(destinatarios),
        "unidade_alvo_id": str(unidade_alvo_id) if unidade_alvo_id else None,
        "nivel_urgencia": nivel_urgencia,
    }