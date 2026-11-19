"""Estado conversacional da sessão (metadados em dados_coletados)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from atendimentos.models import SessaoChat


class FaseChat:
    EXPLORACAO = "exploracao"
    AGUARDANDO_CONFIRMACAO_SERVICO = "aguardando_confirmacao_servico"
    PREENCHIMENTO = "preenchimento"
    REVISAO = "revisao"
    INELEGIVEL = "inelegivel"
    CONCLUIDO = "concluido"

    ALL = frozenset(
        {
            EXPLORACAO,
            AGUARDANDO_CONFIRMACAO_SERVICO,
            PREENCHIMENTO,
            REVISAO,
            INELEGIVEL,
            CONCLUIDO,
        }
    )


_META_KEY = "_meta"


def get_meta(sessao: SessaoChat) -> dict[str, Any]:
    dados = sessao.dados_coletados or {}
    meta = dados.get(_META_KEY)
    if not isinstance(meta, dict):
        meta = {}
    return meta


def get_fase(sessao: SessaoChat) -> str:
    meta = get_meta(sessao)
    raw = str(meta.get("fase") or FaseChat.EXPLORACAO).strip()
    if raw in FaseChat.ALL:
        return raw
    if sessao.servico_identificado_id:
        return FaseChat.PREENCHIMENTO
    return FaseChat.EXPLORACAO


def set_meta(sessao: SessaoChat, **kwargs: Any) -> None:
    dados = dict(sessao.dados_coletados or {})
    meta = dict(get_meta(sessao))
    meta.update(kwargs)
    dados[_META_KEY] = meta
    sessao.dados_coletados = dados


def get_pending_escolha(sessao: SessaoChat) -> dict | None:
    raw = get_meta(sessao).get("pending_escolha")
    return raw if isinstance(raw, dict) else None


def servico_pendente_id(sessao: SessaoChat) -> UUID | None:
    raw = get_meta(sessao).get("servico_pendente_id")
    if not raw:
        return None
    try:
        return UUID(str(raw))
    except (TypeError, ValueError):
        return None


def _primeiro_token(texto: str) -> str:
    import re

    t = (texto or "").strip().lower()
    t = re.sub(r"[^\w\sàáâãéêíóôõúç]", " ", t, flags=re.UNICODE)
    partes = [p for p in t.split() if p]
    return partes[0] if partes else ""


def confirmacao_servico_usuario(texto: str) -> bool | None:
    """True=sim, False=não, None=ambíguo."""
    t = (texto or "").strip().lower()
    if not t:
        return None

    primeiro = _primeiro_token(t)
    positivos = {
        "sim",
        "s",
        "confirmo",
        "confirmar",
        "isso",
        "correto",
        "certo",
        "ok",
        "pode",
        "yes",
        "exato",
        "isso",
    }
    negativos = {"não", "nao", "n", "nope", "negativo", "outro", "errado", "incorreto"}

    if primeiro in positivos:
        return True
    if primeiro in negativos:
        return False

    # Frases do frontend / chat
    frases_sim = (
        "isso mesmo",
        "é isso",
        "e isso",
        "pode ser",
        "isso mesmo!",
        "sim é",
    )
    frases_nao = ("vou explicar", "não é", "nao é", "outro serviço", "outro servico")
    if any(f in t for f in frases_sim):
        return True
    if any(f in t for f in frases_nao):
        return False

    if "confirmar e gerar" in t or "gerar protocolo" in t:
        return True
    return None


def confirmacao_protocolo_usuario(texto: str) -> bool:
    import re

    t = re.sub(r"[^\w\sàáâãéêíóôõúç]", " ", (texto or "").strip().lower())
    t = re.sub(r"\s+", " ", t).strip()
    if not t:
        return False

    gatilhos = (
        "confirmar e gerar",
        "gerar protocolo",
        "gerar o protocolo",
        "confirmar protocolo",
        "confirmo todos",
        "confirmo os dados",
        "pode gerar",
        "pode registrar",
        "pode abrir",
        "está correto",
        "esta correto",
        "tudo certo",
        "__confirmar_protocolo__",
    )
    if any(g in t for g in gatilhos):
        return True
    if "confirmo" in t and ("protocolo" in t or "dados" in t or "tudo" in t):
        return True
    return False


def usuario_pediu_confirmar_protocolo(*, texto: str, confirmar_protocolo: bool) -> bool:
    if confirmar_protocolo:
        return True
    return confirmacao_protocolo_usuario(texto)
