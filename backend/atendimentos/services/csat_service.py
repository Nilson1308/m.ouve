"""Agregações CSAT a partir de ``AvaliacaoProtocolo`` (fonte canônica)."""

from __future__ import annotations

from typing import Any

from django.db.models import Avg, Count, Q, QuerySet

from atendimentos.models import Protocolo


def calcular_resumo_csat(qs: QuerySet) -> dict[str, Any]:
    """KPIs gerais no escopo do queryset (protocolos resolvidos com avaliação)."""
    base = qs.filter(status=Protocolo.Status.RESOLVIDO)
    agg = base.aggregate(
        media_satisfacao=Avg("avaliacao__nota"),
        total_avaliacoes=Count("avaliacao"),
        satisfeitos=Count("id", filter=Q(avaliacao__nota__gte=4)),
    )
    total = int(agg["total_avaliacoes"] or 0)
    media_raw = agg["media_satisfacao"]
    media = round(float(media_raw), 1) if media_raw is not None else None
    pct = (
        round(100.0 * int(agg["satisfeitos"] or 0) / total, 1) if total > 0 else None
    )
    return {
        "media_satisfacao": media,
        "total_avaliacoes": total,
        "percentual_satisfeitos": pct,
    }