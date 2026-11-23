"""Endpoints de lookup para campos dinâmicos do catálogo (PWA / chat)."""

from django.db.models import Q
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalogo.datasources import (
    LOOKUP_DATASOURCE_EQUIPAMENTOS,
    LOOKUP_DATASOURCE_UNIDADES,
)
from catalogo.equipamento_utils import (
    filtrar_equipamentos_busca,
    queryset_equipamentos_ativos,
)
from catalogo.models import UnidadeAdministrativa


class CatalogoLookupUnidadesView(APIView):
    """
    Lista unidades administrativas ativas para campos ``x-ouvia-datasource:
    unidades_administrativas``. Público (mesma política de ``catalogo-servicos``).
    """

    permission_classes = [AllowAny]

    def get(self, request):
        qs = UnidadeAdministrativa.objects.filter(ativo=True).order_by("nome")
        busca = (request.query_params.get("busca") or "").strip()
        if busca:
            qs = qs.filter(
                Q(nome__icontains=busca) | Q(sigla__icontains=busca)
            )
        limite = request.query_params.get("limit")
        try:
            n = int(limite) if limite else 200
        except (TypeError, ValueError):
            n = 200
        n = max(1, min(n, 500))
        qs = qs[:n]
        items = [{"id": str(u.id), "nome": u.nome} for u in qs]
        return Response({"datasource": LOOKUP_DATASOURCE_UNIDADES, "items": items})


class CatalogoLookupEquipamentosView(APIView):
    """
    Lista equipamentos públicos ativos para ``x-ouvia-datasource: equipamentos_publicos``.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        qs = queryset_equipamentos_ativos(
            unidade_id=(request.query_params.get("unidade_id") or "").strip() or None,
            tipo=(request.query_params.get("tipo") or "").strip() or None,
        )
        busca = (request.query_params.get("busca") or "").strip()
        if busca:
            qs = filtrar_equipamentos_busca(qs, busca)
        limite = request.query_params.get("limit")
        try:
            n = int(limite) if limite else 30
        except (TypeError, ValueError):
            n = 30
        n = max(1, min(n, 100))
        items = [
            {
                "id": str(eq.id),
                "nome": eq.nome,
                "tipo": eq.tipo,
                "bairro": eq.bairro or "",
                "unidade_id": str(eq.unidade_responsavel_id),
                "unidade_nome": eq.unidade_responsavel.nome,
            }
            for eq in qs[:n]
        ]
        return Response({"datasource": LOOKUP_DATASOURCE_EQUIPAMENTOS, "items": items})