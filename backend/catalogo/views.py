from django.db.models import Count, Q
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalogo.models import CategoriaCatalogo, ServicoCatalogo
from catalogo.serializers import (
    CategoriaCatalogoSerializer,
    ServicoCatalogoSerializer,
)


def _filtrar_servicos_por_categoria(qs, valor: str):
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


class ServicoCatalogoListView(APIView):
    """Lista serviços ativos do catálogo (com JSON Schema para formulários dinâmicos)."""

    permission_classes = [AllowAny]

    def get(self, request):
        qs = ServicoCatalogo.objects.filter(
            ativo=True,
            is_template=False,
        ).select_related("categoria")
        categoria = request.query_params.get("categoria")
        if categoria:
            qs = _filtrar_servicos_por_categoria(qs, categoria)

        serializer = ServicoCatalogoSerializer(qs, many=True)
        return Response({"servicos": serializer.data})
