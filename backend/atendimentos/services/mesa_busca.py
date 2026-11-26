"""Busca textual da Mesa — suporta múltiplos códigos PROT na mesma string."""

from __future__ import annotations

import re

from django.db.models import Q

_RE_CODIGO = re.compile(r"^[A-Za-z0-9][\w\-/]{2,}$")


def _tokens_busca(texto: str) -> list[str]:
    return [p.strip() for p in re.split(r"[\s,;]+", (texto or "").strip()) if p.strip()]


def filtrar_queryset_busca_protocolo(queryset, termo: str):
    """
    Um termo livre (código ou trecho da descrição) ou vários códigos
    separados por espaço/vírgula (ex.: vindos do Radar IA).
    """
    termo = (termo or "").strip()
    if not termo:
        return queryset
    partes = _tokens_busca(termo)
    if len(partes) > 1 and all(_RE_CODIGO.match(p) for p in partes):
        q = Q()
        for parte in partes:
            q |= Q(codigo__iexact=parte) | Q(codigo__icontains=parte)
        return queryset.filter(q).distinct()
    if len(partes) > 1:
        q = Q()
        for parte in partes:
            q |= Q(codigo__icontains=parte) | Q(descricao__icontains=parte)
        return queryset.filter(q).distinct()
    return queryset.filter(Q(codigo__icontains=termo) | Q(descricao__icontains=termo))