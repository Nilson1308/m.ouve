"""API de notificações internas do backoffice."""

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.backoffice_views import IsBackofficeStaff
from atendimentos.models import NotificacaoInterna
from atendimentos.notificacoes_internas_serializers import NotificacaoInternaSerializer


class NotificacaoInternaListView(APIView):
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request):
        nao_lidas = request.query_params.get("nao_lidas")
        qs = (
            NotificacaoInterna.objects.filter(usuario_destino=request.user)
            .select_related("usuario_destino")
            .order_by("-data_criacao")
        )
        if nao_lidas in ("1", "true", "True", "yes"):
            qs = qs.filter(lida=False)

        limite = request.query_params.get("limit")
        if limite:
            try:
                qs = qs[: max(1, min(int(limite), 200))]
            except ValueError:
                pass

        data = NotificacaoInternaSerializer(qs, many=True).data
        total_nao_lidas = NotificacaoInterna.objects.filter(
            usuario_destino=request.user, lida=False
        ).count()
        return Response(
            {
                "results": data,
                "count": len(data),
                "nao_lidas": total_nao_lidas,
            }
        )


class NotificacaoInternaMarcarLidaView(APIView):
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def post(self, request, notificacao_id):
        notif = get_object_or_404(
            NotificacaoInterna.objects.select_related("usuario_destino"),
            pk=notificacao_id,
            usuario_destino=request.user,
        )
        if not notif.lida:
            notif.lida = True
            notif.save(update_fields=["lida"])
        return Response(
            {
                "sucesso": True,
                "notificacao": NotificacaoInternaSerializer(notif).data,
                "marcada_em": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        )
