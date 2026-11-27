from django.db.models import Count, Q
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalogo.models import CategoriaCatalogo, ServicoCatalogo
from catalogo.catalogo_queries import filtrar_servicos_por_categoria
from catalogo.pwa_catalogo import filtrar_servicos_busca_pwa, queryset_servicos_pwa_publicados
from catalogo.serializers import (
    CategoriaCatalogoSerializer,
    ServicoCatalogoPwaSerializer,
    ServicoCatalogoSerializer,
)


class CategoriaCatalogoListView(APIView):
    """Lista categorias ativas (gestão via Admin)."""

    permission_classes = [AllowAny]

    def get(self, request):
        qs = (
            CategoriaCatalogo.objects.filter(ativo=True)
            .annotate(
                total_servicos=Count(
                    "servicos",
                    filter=Q(servicos__ativo=True, servicos__is_template=False),
                )
            )
            .order_by("ordem", "nome")
        )
        serializer = CategoriaCatalogoSerializer(qs, many=True)
        return Response({"categorias": serializer.data})


def _parse_bool_query(val) -> bool:
    if val is None:
        return False
    return str(val).lower() in ("1", "true", "yes", "sim")


class ServicoCatalogoListView(APIView):
    """Lista serviços ativos do catálogo (com JSON Schema para formulários dinâmicos)."""

    permission_classes = [AllowAny]

    def get(self, request):
        apenas_pwa = _parse_bool_query(request.query_params.get("apenas_visiveis_pwa"))
        if apenas_pwa:
            qs = queryset_servicos_pwa_publicados()
        else:
            qs = ServicoCatalogo.objects.filter(
                ativo=True,
                is_template=False,
            ).select_related("categoria")

        categoria = request.query_params.get("categoria")
        if categoria:
            qs = filtrar_servicos_por_categoria(qs, categoria)

        busca = request.query_params.get("busca")
        if busca:
            qs = filtrar_servicos_busca_pwa(qs, busca)

        if apenas_pwa:
            qs = qs.order_by("ordem_exibicao_pwa", "nome")
            serializer = ServicoCatalogoPwaSerializer(qs, many=True)
        else:
            serializer = ServicoCatalogoSerializer(qs, many=True)
        return Response({"servicos": serializer.data})
