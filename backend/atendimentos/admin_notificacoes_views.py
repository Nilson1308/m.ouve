"""API Super Admin — auditoria e broadcast de notificações internas."""

from __future__ import annotations

import uuid
from datetime import datetime, time

from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.admin_notificacoes_serializers import (
    NotificacaoBroadcastSerializer,
    NotificacaoInternaAuditoriaSerializer,
)
from atendimentos.models import NotificacaoInterna
from atendimentos.notificacoes_broadcast import executar_broadcast_notificacoes
from core_auth.permissions import IsSuperAdmin


class NotificacaoAuditoriaPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


def _parse_bool(value: str | None) -> bool | None:
    if value is None or value == "":
        return None
    return str(value).lower() in ("1", "true", "yes", "sim")


def _parse_instant_param(value: str | None, *, fim_do_dia: bool = False):
    if not value:
        return None
    value = value.strip()
    dt = parse_datetime(value)
    if dt is not None:
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt
    d = parse_date(value)
    if d is None:
        return None
    if fim_do_dia:
        dt = datetime.combine(d, time(23, 59, 59, 999999))
    else:
        dt = datetime.combine(d, time.min)
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def _filtrar_auditoria_notificacoes(request):
    qs = (
        NotificacaoInterna.objects.select_related(
            "usuario_destino",
            "usuario_destino__unidade",
        )
        .order_by("-data_criacao")
    )

    params = request.query_params

    usuario_destino_id = (params.get("usuario_destino_id") or "").strip()
    if usuario_destino_id:
        try:
            qs = qs.filter(usuario_destino_id=uuid.UUID(usuario_destino_id))
        except ValueError:
            raise ValueError("usuario_destino_id inválido (UUID esperado).")

    unidade_destino_id = (params.get("unidade_destino_id") or "").strip()
    if unidade_destino_id:
        try:
            uid = uuid.UUID(unidade_destino_id)
        except ValueError:
            raise ValueError("unidade_destino_id inválido (UUID esperado).")
        qs = qs.filter(usuario_destino__unidade_id=uid)

    lida = _parse_bool(params.get("lida"))
    if lida is not None:
        qs = qs.filter(lida=lida)

    inicio = _parse_instant_param(params.get("data_criacao_inicio"))
    fim = _parse_instant_param(params.get("data_criacao_fim"), fim_do_dia=True)
    if inicio:
        qs = qs.filter(data_criacao__gte=inicio)
    if fim:
        qs = qs.filter(data_criacao__lte=fim)

    busca = (params.get("busca") or "").strip()
    if busca:
        qs = qs.filter(
            Q(titulo__icontains=busca)
            | Q(mensagem__icontains=busca)
            | Q(usuario_destino__nome__icontains=busca)
            | Q(usuario_destino__email__icontains=busca)
        )

    return qs


class NotificacaoAuditoriaView(APIView):
    """GET — todas as notificações internas (auditoria)."""

    permission_classes = [IsAuthenticated, IsSuperAdmin]
    pagination_class = NotificacaoAuditoriaPagination

    def get(self, request):
        try:
            qs = _filtrar_auditoria_notificacoes(request)
        except ValueError as exc:
            return Response({"erro": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request)
        serializer = NotificacaoInternaAuditoriaSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class NotificacaoBroadcastView(APIView):
    """POST — broadcast para servidores ativos (global ou por unidade)."""

    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request):
        ser = NotificacaoBroadcastSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        link = (request.data.get("link_acao") or "").strip()

        try:
            resultado = executar_broadcast_notificacoes(
                titulo=data["titulo"],
                mensagem=data["mensagem"],
                unidade_alvo_id=data.get("unidade_alvo_id"),
                nivel_urgencia=data.get("nivel_urgencia") or "normal",
                link_acao=link,
            )
        except ValueError as exc:
            return Response({"erro": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "sucesso": True,
                **resultado,
            },
            status=status.HTTP_201_CREATED,
        )