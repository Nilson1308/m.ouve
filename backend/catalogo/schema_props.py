"""Validação de extensões JSON Schema do catálogo (lookup, datasources)."""

from __future__ import annotations

from typing import Any

from catalogo.datasources import LOOKUP_DATASOURCES, LOOKUP_UI_WIDGETS, WIDGET_PADRAO


def validar_property_lookup(name: str, prop: dict[str, Any]) -> None:
    """Garante consistência de campos com ``x-ouvia-datasource``."""
    if not isinstance(prop, dict):
        raise ValueError(f"Campo '{name}': property inválida.")
    ds = (prop.get("x-ouvia-datasource") or "").strip()
    if not ds:
        raise ValueError(
            f"Campo '{name}': informe x-ouvia-datasource (ex.: unidades_administrativas)."
        )
    if ds not in LOOKUP_DATASOURCES:
        raise ValueError(
            f"Campo '{name}': datasource '{ds}' não suportado. "
            f"Opções: {', '.join(sorted(LOOKUP_DATASOURCES))}."
        )
    widget = (prop.get("x-ouvia-ui-widget") or WIDGET_PADRAO).strip()
    if widget not in LOOKUP_UI_WIDGETS:
        raise ValueError(
            f"Campo '{name}': widget '{widget}' inválido. "
            f"Use: {', '.join(sorted(LOOKUP_UI_WIDGETS))}."
        )


def validar_schema_formulario_lookup(schema: dict | None) -> None:
    """Valida ``properties`` do JSON Schema publicado/rascunho."""
    if not schema or not isinstance(schema, dict):
        return
    props = schema.get("properties") or {}
    if not isinstance(props, dict):
        raise ValueError("schema_formulario.properties deve ser um objeto.")
    for name, prop in props.items():
        if not isinstance(prop, dict):
            continue
        if prop.get("x-ouvia-datasource"):
            validar_property_lookup(str(name), prop)


def property_tem_lookup_datasource(prop: dict) -> bool:
    return bool((prop.get("x-ouvia-datasource") or "").strip())