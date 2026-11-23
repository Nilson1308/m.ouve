"""Busca e normalização de equipamentos públicos (PWA / slot filling)."""

from __future__ import annotations

import unicodedata
from typing import Any

from django.db.models import Q

from catalogo.datasources import LOOKUP_DATASOURCE_EQUIPAMENTOS
from catalogo.models import EquipamentoPublico


def normalizar_texto_busca(texto: str) -> str:
    s = unicodedata.normalize("NFD", (texto or "").strip())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.casefold()


def _parse_datasource_filter(prop: dict | None) -> dict[str, Any]:
    raw = (prop or {}).get("x-ouvia-datasource-filter") or {}
    return raw if isinstance(raw, dict) else {}


def queryset_equipamentos_ativos(*, unidade_id=None, tipo=None):
    qs = (
        EquipamentoPublico.objects.filter(
            ativo=True,
            unidade_responsavel__ativo=True,
        )
        .select_related("unidade_responsavel")
        .order_by("nome")
    )
    if unidade_id:
        qs = qs.filter(unidade_responsavel_id=unidade_id)
    if tipo:
        qs = qs.filter(tipo=str(tipo).strip())
    return qs


def _coincide_texto(haystack: str, needle: str) -> bool:
    if not needle or not haystack:
        return False
    return normalizar_texto_busca(needle) in normalizar_texto_busca(haystack)


def equipamento_coincide_busca(equipamento: EquipamentoPublico, busca: str) -> bool:
    termo = (busca or "").strip()
    if not termo:
        return True
    if _coincide_texto(equipamento.nome, termo):
        return True
    if equipamento.bairro and _coincide_texto(equipamento.bairro, termo):
        return True
    for alias in equipamento.apelidos or []:
        if isinstance(alias, str) and _coincide_texto(alias, termo):
            return True
    return False


def filtrar_equipamentos_busca(qs, busca: str):
    termo = (busca or "").strip()
    if not termo:
        return qs
    base = qs.filter(Q(nome__icontains=termo) | Q(bairro__icontains=termo))
    ids_base = set(base.values_list("pk", flat=True))
    extra_ids: list[Any] = []
    for eq in qs.exclude(pk__in=ids_base).only("id", "nome", "bairro", "apelidos"):
        if equipamento_coincide_busca(eq, termo):
            extra_ids.append(eq.pk)
    if extra_ids:
        return qs.filter(Q(pk__in=ids_base) | Q(pk__in=extra_ids)).distinct()
    return base.distinct()


def campos_schema_datasource(schema: dict | None, datasource: str) -> list[str]:
    props = (schema or {}).get("properties") or {}
    if not isinstance(props, dict):
        return []
    chaves: list[str] = []
    for nome, prop in props.items():
        if not isinstance(prop, dict):
            continue
        ds = (prop.get("x-ouvia-datasource") or "").strip()
        if ds == datasource:
            chaves.append(str(nome))
    return chaves


def campos_equipamentos_publicos_schema(schema: dict | None) -> list[str]:
    return campos_schema_datasource(schema, LOOKUP_DATASOURCE_EQUIPAMENTOS)


def texto_contem_equipamento(texto: str, equipamento: EquipamentoPublico) -> bool:
    termos = [equipamento.nome] + [
        str(a).strip() for a in (equipamento.apelidos or []) if str(a).strip()
    ]
    for termo in termos:
        if len(normalizar_texto_busca(termo)) < 4:
            continue
        if _coincide_texto(texto, termo):
            return True
    return False


def buscar_equipamentos_unicos_no_texto(
    texto: str,
    *,
    unidade_id=None,
    tipo=None,
) -> list[EquipamentoPublico]:
    qs = queryset_equipamentos_ativos(unidade_id=unidade_id, tipo=tipo)
    encontrados: list[EquipamentoPublico] = []
    for eq in qs:
        if texto_contem_equipamento(texto, eq):
            encontrados.append(eq)
    return encontrados