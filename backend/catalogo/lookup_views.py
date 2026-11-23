"""Endpoints de lookup para campos dinâmicos do catálogo (PWA / chat)."""

from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalogo.datasources import (
    LOOKUP_DATASOURCE_EQUIPAMENTOS,
    LOOKUP_DATASOURCE_UNIDADES,
)
from catalogo.equipamento_utils import (
    CoordenadasInvalidasError,
    distancia_em_metros,
    filtrar_equipamentos_busca,
    parse_lat_lng_query,
    queryset_equipamentos_ativos,
    queryset_equipamentos_por_proximidade,
    serializar_equipamento_lookup_item,
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

        try:
            _, _, ref = parse_lat_lng_query(
                request.query_params.get("lat"),
                request.query_params.get("lng"),
                exigir_par=True,
            )
        except CoordenadasInvalidasError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        ordenar_por_distancia = ref is not None
        if ordenar_por_distancia:
            qs = queryset_equipamentos_por_proximidade(qs, ref)

        limite = request.query_params.get("limit")
        try:
            n = int(limite) if limite else 30
        except (TypeError, ValueError):
            n = 30
        n = max(1, min(n, 100))
        resultados = list(qs[:n])

        items = []
        for eq in resultados:
            distancia_metros = None
            if ordenar_por_distancia:
                distancia_metros = distancia_em_metros(getattr(eq, "distancia", None))
            items.append(
                serializar_equipamento_lookup_item(
                    eq,
                    distancia_metros=distancia_metros,
                    incluir_distancia=ordenar_por_distancia,
                )
            )
        return Response({"datasource": LOOKUP_DATASOURCE_EQUIPAMENTOS, "items": items})