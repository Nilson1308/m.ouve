"""API Super Admin — singleton ConfiguracaoSistema."""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.configuracao_sistema_serializers import ConfiguracaoSistemaSerializer
from atendimentos.models import ConfiguracaoSistema
from core_auth.permissions import IsSuperAdmin


class ConfiguracaoSistemaAdminView(APIView):
    """GET/PATCH da configuração global (gatilhos de notificação, IA, etc.)."""

    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        cfg = ConfiguracaoSistema.load()
        return Response(ConfiguracaoSistemaSerializer(cfg).data)

    def patch(self, request):
        cfg = ConfiguracaoSistema.load()
        ser = ConfiguracaoSistemaSerializer(cfg, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)