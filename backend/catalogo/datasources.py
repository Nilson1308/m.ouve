"""Fontes de dados para campos lookup do formulário (`x-ouvia-datasource`)."""

from __future__ import annotations

LOOKUP_DATASOURCES = frozenset(
    {
        "unidades_administrativas",
    }
)

LOOKUP_UI_WIDGETS = frozenset(
    {
        "searchable_select",
        "select",
    }
)

WIDGET_PADRAO = "searchable_select"