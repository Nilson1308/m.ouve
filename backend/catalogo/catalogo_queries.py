"""Consultas compartilhadas do catálogo (filtros por categoria)."""

from django.db.models import Q


def filtrar_servicos_por_categoria(qs, valor: str):
    """Aceita slug, nome ou alias legado ``ouvidoria`` / ``zeladoria``."""
    raw = (valor or "").strip()
    if not raw:
        return qs

    legado = raw.lower()
    if legado in ("ouvidoria", "zeladoria"):
        return qs.filter(categoria__tipo_legado=legado)

    slug = legado.replace(" ", "_")
    return qs.filter(
        Q(categoria__slug__iexact=slug)
        | Q(categoria__nome__iexact=raw)
    )