"""Dashboard — métricas de inelegibilidade (sessões bloqueadas pela IA)."""

from __future__ import annotations

from typing import Any

from django.core.exceptions import PermissionDenied
from django.db.models import Count

from atendimentos.models import SessaoChat
from atendimentos.services.analytics_service import _query_params_dict
from atendimentos.services.escopo_dados import aplicar_escopo_sessoes_chat, escopo_dashboard
from atendimentos.services.mapa_calor_service import _parse_data_fim, _parse_data_inicio
from django.utils import timezone


def queryset_sessoes_inelegiveis_escopo(user):
    """Sessões com bloqueio registrado (motivo persistido)."""
    qs = SessaoChat.objects.filter(motivo_inelegibilidade__isnull=False).exclude(
        motivo_inelegibilidade=""
    )
    qs = aplicar_escopo_sessoes_chat(user, qs)
    return qs.select_related("servico_identificado", "servico_identificado__categoria")


def _aplicar_filtros_periodo_unidade(qs, user, params: dict) -> tuple[Any, dict[str, Any]]:
    escopo = escopo_dashboard(user)
    filtros: dict[str, Any] = {}

    req_unidade = (params.get("unidade_responsavel_id") or "").strip() or None
    if escopo["tipo"] == "unidade" and escopo["unidade_id"]:
        if req_unidade and str(req_unidade) != str(escopo["unidade_id"]):
            raise PermissionDenied(
                "Consulta restrita à sua unidade administrativa."
            )
    elif req_unidade:
        qs = qs.filter(servico_identificado__unidade_responsavel_id=req_unidade)
        filtros["unidade_responsavel_id"] = req_unidade

    data_inicio = _parse_data_inicio(params.get("data_inicio"))
    data_fim = _parse_data_fim(params.get("data_fim"))
    if data_inicio:
        qs = qs.filter(criado_em__gte=data_inicio)
        filtros["data_inicio"] = data_inicio.isoformat()
    if data_fim:
        qs = qs.filter(criado_em__lte=data_fim)
        filtros["data_fim"] = data_fim.isoformat()

    servico_id = (params.get("servico_id") or "").strip() or None
    if servico_id:
        qs = qs.filter(servico_identificado_id=servico_id)
        filtros["servico_id"] = servico_id

    categoria_id = (params.get("categoria_id") or "").strip() or None
    if categoria_id:
        qs = qs.filter(servico_identificado__categoria_id=categoria_id)
        filtros["categoria_id"] = categoria_id

    return qs, filtros


def dashboard_inelegibilidade(user, query_params=None) -> dict[str, Any]:
    escopo = escopo_dashboard(user)
    params = _query_params_dict(query_params)
    qs = queryset_sessoes_inelegiveis_escopo(user)
    qs, filtros_aplicados = _aplicar_filtros_periodo_unidade(qs, user, params)

    total = qs.count()

    ranking_servicos = list(
        qs.values(
            "servico_identificado_id",
            "servico_identificado__nome",
        )
        .annotate(total=Count("id"))
        .order_by("-total", "servico_identificado__nome")
    )
    por_servico = []
    for row in ranking_servicos:
        sid = row["servico_identificado_id"]
        nome = (row["servico_identificado__nome"] or "Sem serviço").strip()
        label = f"{nome}: {row['total']} bloqueio(s)"
        por_servico.append(
            {
                "servico_id": str(sid) if sid else None,
                "servico_nome": nome,
                "total": row["total"],
                "rotulo": label,
            }
        )

    ranking_motivos = list(
        qs.values("motivo_inelegibilidade")
        .annotate(total=Count("id"))
        .order_by("-total", "motivo_inelegibilidade")
    )
    por_motivo = [
        {
            "motivo": row["motivo_inelegibilidade"],
            "total": row["total"],
        }
        for row in ranking_motivos
    ]

    return {
        "escopo": escopo["tipo"],
        "unidade_id": str(escopo["unidade_id"]) if escopo["unidade_id"] else None,
        "gerado_em": timezone.now().isoformat(),
        "filtros_aplicados": filtros_aplicados,
        "total_sessoes_inelegiveis": total,
        "ranking_por_servico": por_servico,
        "ranking_por_motivo": por_motivo,
    }