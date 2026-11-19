"""API PWA — notificações in-app e Web Push subscribe."""

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.models import NotificacaoCidadao
from atendimentos.notificacoes_cidadao_serializers import (
    NotificacaoCidadaoSerializer,
    PushSubscribeSerializer,
    PushSubscriptionResponseSerializer,
)
from atendimentos.vapid_keys import get_configured_vapid_public_key


class NotificacaoCidadaoListView(APIView):
    """GET /api/v1/app/notificacoes — lista + contador ``nao_lidas``."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        nao_lidas_q = request.query_params.get("nao_lidas")
        qs = (
            NotificacaoCidadao.objects.filter(usuario=request.user)
            .select_related("protocolo")
            .order_by("-criada_em")
        )
        if nao_lidas_q in ("1", "true", "True", "yes"):
            qs = qs.filter(lida=False)

        limite = request.query_params.get("limit")
        if limite:
            try:
                qs = qs[: max(1, min(int(limite), 200))]
            except ValueError:
                pass

        total_nao_lidas = NotificacaoCidadao.objects.filter(
            usuario=request.user, lida=False
        ).count()
        data = NotificacaoCidadaoSerializer(qs, many=True).data
        response = Response(
            {
                "results": data,
                "count": len(data),
                "nao_lidas": total_nao_lidas,
            }
        )
        response["X-Notificacoes-Nao-Lidas"] = str(total_nao_lidas)
        return response


class NotificacaoCidadaoMarcarLidaView(APIView):
    """PATCH /api/v1/app/notificacoes/<id>/marcar-lida"""

    permission_classes = [IsAuthenticated]

    def patch(self, request, notificacao_id):
        notif = get_object_or_404(
            NotificacaoCidadao.objects.select_related("protocolo"),
            pk=notificacao_id,
            usuario=request.user,
        )
        if not notif.lida:
            notif.lida = True
            notif.save(update_fields=["lida"])
        return Response(
            {
                "sucesso": True,
                "notificacao": NotificacaoCidadaoSerializer(notif).data,
                "marcada_em": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            status=status.HTTP_200_OK,
        )


class PushSubscribeView(APIView):
    """POST /api/v1/app/notificacoes/push-subscribe"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PushSubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sub = serializer.save(usuario=request.user)
        return Response(
            PushSubscriptionResponseSerializer(sub).data,
            status=status.HTTP_201_CREATED,
        )


class VapidPublicKeyView(APIView):
    """GET /api/v1/app/notificacoes/vapid-public-key — chave pública para ``pushManager.subscribe``."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        key = get_configured_vapid_public_key()
        if not key:
            return Response(
                {
                    "configurado": False,
                    "vapid_public_key": None,
                    "detail": "Web Push não configurado no servidor (VAPID).",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(
            {
                "configurado": True,
                "vapid_public_key": key,
            }
        )