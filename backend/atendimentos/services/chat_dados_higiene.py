"""Limpeza de metadados internos antes de validar / persistir protocolo."""

from __future__ import annotations

from typing import Any

CHAVE_EQUIPAMENTO_TEXTO_LIVRE = "equipamento_texto_livre"
FORMATO_NAO_CATALOGADO = "nao_catalogado"


def valor_equipamento_nao_catalogado(valor: Any) -> str | None:
    """Extrai texto citado fora do catálogo (dict ou string auxiliar)."""
    if isinstance(valor, dict) and valor.get(FORMATO_NAO_CATALOGADO):
        texto = (valor.get("texto") or "").strip()
        return texto[:180] if texto else None
    if isinstance(valor, str) and valor.strip().startswith("{"):
        return None
    return None


def extrair_equipamento_citado_sessao(dados: dict | None) -> str:
    citado = (dados or {}).get("_equipamento_citado_nao_catalogado") or ""
    if isinstance(citado, str) and citado.strip():
        return citado.strip()[:180]
    for chave, valor in (dados or {}).items():
        if str(chave).startswith("_"):
            continue
        if isinstance(valor, dict) and valor.get(FORMATO_NAO_CATALOGADO):
            t = (valor.get("texto") or "").strip()
            if t:
                return t[:180]
    aux = (dados or {}).get(CHAVE_EQUIPAMENTO_TEXTO_LIVRE)
    if isinstance(aux, str) and aux.strip():
        return aux.strip()[:180]
    return ""


def higienizar_dados_para_protocolo(dados: dict | None) -> dict:
    """Remove chaves internas (_*) e valores de lookup não catalogados do JSON do protocolo."""
    if not dados:
        return {}
    out: dict = {}
    for chave, valor in dados.items():
        if str(chave).startswith("_"):
            continue
        if chave in (CHAVE_EQUIPAMENTO_TEXTO_LIVRE, "_campos_pulados"):
            continue
        if isinstance(valor, dict) and valor.get(FORMATO_NAO_CATALOGADO):
            continue
        out[chave] = valor
    return out