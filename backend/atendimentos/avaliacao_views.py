"""API de avaliação de satisfação pós-protocolo (CSAT)."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.avaliacao_serializers import (
    AvaliacaoProtocoloSerializer,
    AvaliarProtocoloAppSerializer,
)
from atendimentos.models import AvaliacaoProtocolo, Protocolo


def _protocolo_do_cidadao(request, protocolo_id):
    """Resolve protocolo por UUID ou código (PROT-…), como no ProtocoloViewSet."""
    qs = Protocolo.objects.select_related("servico").filter(usuario=request.user)
    lookup = str(protocolo_id)
    if lookup.upper().startswith("PROT-"):
        return get_object_or_404(qs, codigo=lookup)
    return get_object_or_404(qs, pk=protocolo_id)


def _resposta_avaliacao(avaliacao: AvaliacaoProtocolo) -> dict:
    return {
        "id": str(avaliacao.id),
        "protocolo_id": str(avaliacao.protocolo_id),
        "nota": avaliacao.nota,
        "comentario": avaliacao.comentario or "",
        "criada_em": avaliacao.criada_em.strftime("%Y-%m-%dT%H:%M:%SZ")
        if avaliacao.criada_em
        else None,
    }


def _resposta_avaliacao_pwa(protocolo: Protocolo, avaliacao: AvaliacaoProtocolo) -> dict:
    """Payload enxuto para o PWA."""
    from atendimentos.services.reabertura_service import avaliar_elegibilidade_reabertura

    eleg = avaliar_elegibilidade_reabertura(protocolo)
    return {
        "nota": avaliacao.nota,
        "comentario": avaliacao.comentario or "",
        "criada_em": avaliacao.criada_em.strftime("%Y-%m-%dT%H:%M:%SZ")
        if avaliacao.criada_em
        else None,
        "pode_reabrir": eleg.pode,
        "sugerir_reabertura_csat": eleg.sugerir_reabertura_csat,
    }


class CriarAvaliacaoView(APIView):
    """Legado — ``POST /api/v1/avaliacoes``."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AvaliacaoProtocoloSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        avaliacao = serializer.save()
        return Response(_resposta_avaliacao(avaliacao), status=status.HTTP_201_CREATED)


class AvaliarProtocoloAppView(APIView):
    """``POST /api/v1/app/protocolos/<id>/avaliar/`` — PWA cidadão."""

    permission_classes = [IsAuthenticated]

    def post(self, request, protocolo_id):
        protocolo = _protocolo_do_cidadao(request, protocolo_id)
        serializer = AvaliarProtocoloAppSerializer(
            data=request.data,
            context={"request": request, "protocolo": protocolo},
        )
        serializer.is_valid(raise_exception=True)
        avaliacao = serializer.save()
        protocolo.refresh_from_db()
        return Response(
            _resposta_avaliacao_pwa(protocolo, avaliacao),
            status=status.HTTP_201_CREATED,
        )