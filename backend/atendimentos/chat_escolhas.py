"""Normalização de escolhas via UI (single/multi/outro)."""

from __future__ import annotations

from catalogo.models import ServicoCatalogo


def normalizar_dados_slot(servico: ServicoCatalogo, dados_slot: dict | None) -> dict:
    if not dados_slot or not isinstance(dados_slot, dict):
        return {}
    schema = servico.schema_formulario or {}
    props = schema.get("properties") or {}
    limpos: dict = {}
    for chave, valor in dados_slot.items():
        if str(chave).startswith("_"):
            continue
        if chave.endswith("_outro"):
            if isinstance(valor, str) and valor.strip():
                limpos[chave] = valor.strip()
            continue
        prop = props.get(chave) or {}
        if prop.get("type") == "array":
            if isinstance(valor, str):
                valor = [v.strip() for v in valor.split(",") if v.strip()]
            if isinstance(valor, list):
                limpos[chave] = [str(v) for v in valor if str(v).strip()]
            elif valor is not None and str(valor).strip():
                limpos[chave] = [str(valor).strip()]
            continue
        if (prop.get("x-ouvia-selection") or "").lower() == "multi":
            if isinstance(valor, str):
                valor = [v.strip() for v in valor.split(",") if v.strip()]
            if isinstance(valor, list):
                limpos[chave] = [str(v) for v in valor if str(v).strip()]
            continue
        else:
            if isinstance(valor, list):
                valor = valor[0] if valor else None
            if valor is None or (isinstance(valor, str) and not valor.strip()):
                continue
            limpos[chave] = str(valor).strip()
    return limpos
