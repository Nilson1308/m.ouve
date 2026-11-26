"""API — matriz de urgência e alteração em protocolo."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.backoffice_serializers import BackofficeProtocoloDetalheSerializer
from atendimentos.configuracao_matriz_urgencia_serializers import (
    ConfiguracaoMatrizUrgenciaSerializer,
)
from atendimentos.models import ConfiguracaoMatrizUrgencia, Protocolo
from atendimentos.services.escopo_dados import queryset_protocolos_escopo
from atendimentos.services.matriz_urgencia_service import alterar_urgencia_protocolo
from core_auth.permissions import IsBackofficeStaff
from core_auth.rbac import make_has_module_permission


class ConfiguracaoMatrizUrgenciaView(APIView):
    def get_permissions(self):
        acao = "editar" if self.request.method in ("PATCH", "PUT") else "ler"
        return [
            IsAuthenticated(),
            IsBackofficeStaff(),
            make_has_module_permission("configuracoes", acao)(),
        ]

    def get(self, request):
        cfg = ConfiguracaoMatrizUrgencia.load()
        return Response(ConfiguracaoMatrizUrgenciaSerializer(cfg).data)

    def patch(self, request):
        cfg = ConfiguracaoMatrizUrgencia.load()
        ser = ConfiguracaoMatrizUrgenciaSerializer(cfg, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)


class ProtocoloUrgenciaView(APIView):
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def post(self, request, protocolo_id):
        protocolo = get_object_or_404(
            queryset_protocolos_escopo(request.user),
            pk=protocolo_id,
        )
        data = request.data or {}
        protocolo = alterar_urgencia_protocolo(
            protocolo,
            user=request.user,
            urgencia=data.get("urgencia"),
            acao=data.get("acao"),
            justificativa=data.get("justificativa") or "",
        )
        return Response(
            BackofficeProtocoloDetalheSerializer(
                protocolo, context={"request": request}
            ).data,
            status=status.HTTP_200_OK,
        )