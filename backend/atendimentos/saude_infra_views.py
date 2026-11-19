"""GET saúde da infraestrutura de mensageria (Redis + Celery) — Super Admin."""

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.saude_infra import montar_relatorio_saude_infra
from core_auth.permissions import IsSuperAdmin


class SaudeInfraAdminView(APIView):
    """
    Monitoramento em tempo real para o painel «Saúde do Chat».
    Checagens com timeout curto para não travar o backoffice.
    """

    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        return Response(montar_relatorio_saude_infra())