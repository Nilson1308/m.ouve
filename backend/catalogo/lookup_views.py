"""Endpoints de lookup para campos dinâmicos do catálogo (PWA / chat)."""

from django.db.models import Q
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

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
        return Response({"datasource": "unidades_administrativas", "items": items})