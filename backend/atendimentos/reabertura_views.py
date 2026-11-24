"""POST reabertura de protocolo — PWA cidadão."""

from django.core.exceptions import ValidationError
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.models import Protocolo
from atendimentos.serializers import ProtocoloDetailSerializer
from atendimentos.services.reabertura_service import reabrir_protocolo, serializar_reabertura


class ReabrirProtocoloSerializer(serializers.Serializer):
    motivo = serializers.CharField(min_length=10, max_length=5000)
    anexos_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )


class ProtocoloReabrirMixin:
    def reabrir_protocolo_cidadao(self, request, protocolo: Protocolo):
        if protocolo.usuario_id != request.user.id:
            return Response(
                {"detail": "Protocolo não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        ser = ReabrirProtocoloSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            reabertura = reabrir_protocolo(
                protocolo,
                request.user,
                motivo=ser.validated_data["motivo"],
                anexos_ids=ser.validated_data.get("anexos_ids"),
                request=request,
            )
        except ValidationError as exc:
            detail = exc.message_dict if hasattr(exc, "message_dict") else {"detail": str(exc)}
            if "detail" in detail:
                return Response(detail, status=status.HTTP_400_BAD_REQUEST)
            return Response(detail, status=status.HTTP_400_BAD_REQUEST)

        protocolo.refresh_from_db()
        return Response(
            {
                "reabertura": serializar_reabertura(reabertura, request=request),
                "protocolo": ProtocoloDetailSerializer(
                    protocolo, context={"request": request}
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )