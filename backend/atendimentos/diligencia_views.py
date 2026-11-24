"""APIs de diligência (backoffice e PWA)."""

from __future__ import annotations

from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.backoffice_services import get_protocolo_backoffice
from atendimentos.models import DiligenciaProtocolo
from atendimentos.services.diligencia_service import (
    abrir_diligencia,
    cancelar_diligencia,
    diligencia_aguardando,
    responder_diligencia,
)
from core_auth.permissions import IsBackofficeStaff, PermissaoMesaTrabalho


class AbrirDiligenciaSerializer(serializers.Serializer):
    pergunta = serializers.CharField()
    exige_anexo = serializers.BooleanField(required=False, default=False)
    ordem_servico_id = serializers.UUIDField(required=False, allow_null=True)


class CancelarDiligenciaSerializer(serializers.Serializer):
    motivo = serializers.CharField(required=False, allow_blank=True, default="")


class ResponderDiligenciaSerializer(serializers.Serializer):
    resposta = serializers.CharField()
    anexos_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list,
    )


class BackofficeAbrirDiligenciaView(APIView):
    permission_classes = [IsAuthenticated, PermissaoMesaTrabalho]

    def post(self, request, protocolo_id):
        protocolo = get_protocolo_backoffice(protocolo_id, user=request.user)
        ser = AbrirDiligenciaSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        unidade_id = getattr(request.user, "unidade_id", None)
        if not unidade_id:
            return Response(
                {"detail": "Servidor sem unidade vinculada não pode abrir diligência."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        diligencia = abrir_diligencia(
            protocolo,
            autor=request.user,
            unidade_solicitante_id=unidade_id,
            pergunta=ser.validated_data["pergunta"],
            exige_anexo=ser.validated_data.get("exige_anexo", False),
            ordem_servico_id=ser.validated_data.get("ordem_servico_id"),
            request=request,
        )
        from atendimentos.services.diligencia_service import serializar_diligencia_resumo

        return Response(serializar_diligencia_resumo(diligencia), status=status.HTTP_201_CREATED)


class BackofficeCancelarDiligenciaView(APIView):
    permission_classes = [IsAuthenticated, PermissaoMesaTrabalho]

    def post(self, request, diligencia_id):
        try:
            diligencia = DiligenciaProtocolo.objects.select_related("protocolo").get(
                pk=diligencia_id
            )
        except DiligenciaProtocolo.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        get_protocolo_backoffice(diligencia.protocolo_id, user=request.user)

        ser = CancelarDiligenciaSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        diligencia = cancelar_diligencia(
            diligencia_id,
            autor=request.user,
            motivo=ser.validated_data.get("motivo") or "",
            request=request,
        )
        from atendimentos.services.diligencia_service import serializar_diligencia_resumo

        return Response(serializar_diligencia_resumo(diligencia))


class ProtocoloResponderDiligenciaMixin:
    """POST responder-diligencia no viewset de protocolos (PWA)."""

    def responder_diligencia_protocolo(self, request, protocolo):
        if protocolo.usuario_id != request.user.pk:
            return Response(status=status.HTTP_403_FORBIDDEN)

        diligencia = diligencia_aguardando(protocolo)
        if not diligencia:
            return Response(
                {"detail": "Não há diligência aguardando resposta."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ser = ResponderDiligenciaSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        diligencia = responder_diligencia(
            protocolo,
            diligencia.id,
            resposta=ser.validated_data["resposta"],
            anexos_ids=ser.validated_data.get("anexos_ids"),
            request=request,
        )
        from atendimentos.services.diligencia_service import serializar_diligencia_resumo

        return Response(serializar_diligencia_resumo(diligencia), status=status.HTTP_200_OK)