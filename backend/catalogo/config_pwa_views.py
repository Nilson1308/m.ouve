"""GET público — configuração de abertura do PWA."""

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalogo.pwa_catalogo import obter_config_pwa_cached


class CatalogoConfigPwaView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(obter_config_pwa_cached())