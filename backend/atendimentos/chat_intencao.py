"""Detecção de intenção de pular campo ou declarar «não sei» no chat."""

from __future__ import annotations

import re
from typing import Any


_FRASES_DECLINIO = (
    "não sei",
    "nao sei",
    "sem observação",
    "sem observacao",
    "sem observações",
    "sem observacoes",
    "nada",
    "nenhum",
    "nenhuma",
    "não tenho",
    "nao tenho",
    "pular",
    "não se aplica",
    "nao se aplica",
    "dispenso",
    "só isso",
    "so isso",
    "não preciso",
    "nao preciso",
    "sem foto",
    "sem fotos",
    "sem imagem",
    "não quero",
    "nao quero",
    "pode seguir",
    "pode continuar",
)


def _normalizar_declinio(texto: str) -> str:
    t = re.sub(r"[^\w\sàáâãéêíóôõúç]", " ", (texto or "").strip().lower())
    return re.sub(r"\s+", " ", t).strip()


def detectar_intencao_pular_ou_nao_sei(
    texto: str,
    *,
    campo: str | None = None,
    obrigatorio: bool = False,
    usar_llm: bool = True,
    extracao_llm: dict | None = None,
) -> bool:
    """
    Retorna True se o cidadão quer pular ou não possui a informação (somente útil em opcionais).
    Camada rápida + flag intencao_pular vinda da extração LLM no mesmo turno.
    """
    if obrigatorio:
        return False
    t = _normalizar_declinio(texto)
    if not t or len(t) > 160:
        return False
    if re.search(r"\d{3,}", t):
        return False
    if any(f in t for f in _FRASES_DECLINIO):
        return True
    if t in ("n/a", "na", "não", "nao"):
        return True
    if extracao_llm and extracao_llm.get("intencao_pular") is True:
        return True
    return False