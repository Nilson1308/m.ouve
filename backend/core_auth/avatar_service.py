"""Validação, persistência e remoção de avatares de usuário."""

from __future__ import annotations

import logging

from django.core.files.storage import default_storage

from rest_framework import serializers

logger = logging.getLogger(__name__)

AVATAR_MAX_BYTES = 2 * 1024 * 1024
AVATAR_MIMES = frozenset({"image/jpeg", "image/png", "image/webp"})


def _normalizar_mime(content_type: str) -> str:
    return (content_type or "").split(";")[0].strip().lower()


def validar_arquivo_avatar(arquivo) -> None:
    """Levanta ValidationError se o arquivo violar regras de avatar."""
    if arquivo is None:
        raise serializers.ValidationError({"avatar": "Envie o arquivo no campo «avatar»."})

    tamanho = getattr(arquivo, "size", None)
    if tamanho is not None and tamanho > AVATAR_MAX_BYTES:
        raise serializers.ValidationError(
            {"avatar": "A imagem deve ter no máximo 2 MB."}
        )

    mime = _normalizar_mime(getattr(arquivo, "content_type", "") or "")
    if mime not in AVATAR_MIMES:
        raise serializers.ValidationError(
            {
                "avatar": (
                    "Formato não suportado. Envie uma imagem JPEG, PNG ou WebP."
                )
            }
        )


def _apagar_arquivo_por_nome(nome: str | None) -> None:
    if not nome:
        return
    try:
        if default_storage.exists(nome):
            default_storage.delete(nome)
    except Exception:
        logger.warning("Falha ao remover avatar antigo: %s", nome, exc_info=True)


def substituir_avatar(usuario, arquivo) -> None:
    """Persiste novo avatar e remove arquivo anterior do storage."""
    validar_arquivo_avatar(arquivo)
    nome_anterior = usuario.avatar.name if usuario.avatar else None
    usuario.avatar = arquivo
    usuario.save(update_fields=["avatar", "updated_at"])
    if nome_anterior and nome_anterior != (usuario.avatar.name if usuario.avatar else None):
        _apagar_arquivo_por_nome(nome_anterior)


def remover_avatar(usuario) -> None:
    """Remove avatar do usuário e apaga o arquivo (ignora se inexistente)."""
    if not usuario.avatar:
        return
    try:
        usuario.avatar.delete(save=True)
    except Exception:
        logger.warning("Falha ao apagar avatar do usuário %s", usuario.pk, exc_info=True)
        usuario.avatar = None
        usuario.save(update_fields=["avatar", "updated_at"])