"""Níveis canônicos de urgência — Sprint 4.6."""

from __future__ import annotations

NIVEIS = ("baixa", "normal", "alta", "critica")

PESO_POR_NIVEL: dict[str, int] = {
    "baixa": 1,
    "normal": 2,
    "alta": 3,
    "critica": 4,
}

_ALIASES_LEGADO: dict[str, str] = {
    "baixa": "baixa",
    "low": "baixa",
    "normal": "normal",
    "media": "normal",
    "média": "normal",
    "medio": "normal",
    "médio": "normal",
    "alta": "alta",
    "high": "alta",
    "urgente": "alta",
    "critica": "critica",
    "crítica": "critica",
    "critical": "critica",
    "emergencia": "critica",
    "emergência": "critica",
}


def normalizar_nivel(valor: str | None, *, padrao: str = "normal") -> str:
    if not valor:
        return padrao
    chave = str(valor).strip().lower()
    return _ALIASES_LEGADO.get(chave, padrao if chave not in PESO_POR_NIVEL else chave)


def peso_nivel(nivel: str | None) -> int:
    return PESO_POR_NIVEL.get(normalizar_nivel(nivel), 2)


def nivel_maior(a: str | None, b: str | None) -> str:
    na = normalizar_nivel(a)
    nb = normalizar_nivel(b)
    return na if peso_nivel(na) >= peso_nivel(nb) else nb