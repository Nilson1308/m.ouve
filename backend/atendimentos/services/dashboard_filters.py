"""Filtros compartilhados dos dashboards executivos (Sprint 5)."""

from __future__ import annotations

from django.db.models import Q, QuerySet

from atendimentos.services.protocolo_localidade import (
    bairro_de_dados_dinamicos,
    bairro_de_endereco_texto,
)


def aplicar_filtro_bairro(qs: QuerySet, bairro_param) -> tuple[QuerySet, str | None]:
    """
    Filtra por bairro usando múltiplas fontes alinhadas ao cadastro real:
    ``dados_dinamicos.bairro``, ``endereco_texto`` e ``usuario.endereco.bairro``.
    """
    bairro = (bairro_param or "").strip()
    if not bairro:
        return qs, None
    qs = qs.filter(
        Q(dados_dinamicos__bairro__iexact=bairro)
        | Q(dados_dinamicos__bairro__icontains=bairro)
        | Q(endereco_texto__icontains=bairro)
        | Q(usuario__endereco__bairro__iexact=bairro)
        | Q(usuario__endereco__bairro__icontains=bairro)
    ).distinct()
    return qs, bairro


def listar_bairros_protocolos(user, *, apenas_com_geo: bool = False) -> list[str]:
    """
    Bairros distintos no escopo RBAC — ``dados_dinamicos.bairro`` e fallbacks.
    """
    from atendimentos.services.analytics_service import queryset_protocolos_escopo

    qs = queryset_protocolos_escopo(user)
    if apenas_com_geo:
        qs = qs.filter(localizacao__isnull=False)
    nomes: set[str] = set()

    for dados, endereco in qs.values_list("dados_dinamicos", "endereco_texto").iterator():
        b = bairro_de_dados_dinamicos(dados) or bairro_de_endereco_texto(endereco or "")
        if b:
            nomes.add(b)

    for b in (
        qs.exclude(usuario__endereco__bairro__exact="")
        .values_list("usuario__endereco__bairro", flat=True)
        .distinct()
        .iterator()
    ):
        b = (b or "").strip()
        if b:
            nomes.add(b)

    return sorted(nomes, key=lambda s: s.casefold())


def listar_bairros_dashboard(user) -> list[str]:
    """Lista GIS — somente protocolos com coordenadas."""
    return listar_bairros_protocolos(user, apenas_com_geo=True)