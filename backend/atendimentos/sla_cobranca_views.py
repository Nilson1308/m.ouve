"""APIs — SLA, cobrança e relatórios (backoffice)."""

from __future__ import annotations

from uuid import UUID

from django.http import HttpResponse
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.configuracao_sla_cobranca_serializers import ConfiguracaoSlaCobrancaSerializer
from atendimentos.models import ConfiguracaoSlaCobranca, RelatorioSlaEnvio
from atendimentos.services.sla_cobranca_service import (
    avaliar_elegibilidade_cobranca,
    dias_atraso,
    enviar_digest_sla_atrasados,
    exportar_csv_relatorio_atrasados,
    filtrar_relatorio_atrasados,
    prazo_sla_dt,
    resumo_relatorio_atrasados,
    serializar_item_relatorio,
)
from core_auth.permissions import PermissaoConfiguracoes, PermissaoMesaTrabalho


class ConfiguracaoSlaCobrancaView(APIView):
    permission_classes = [IsAuthenticated, PermissaoConfiguracoes]

    def get(self, request):
        cfg = ConfiguracaoSlaCobranca.load()
        return Response(ConfiguracaoSlaCobrancaSerializer(cfg).data)

    def patch(self, request):
        cfg = ConfiguracaoSlaCobranca.load()
        ser = ConfiguracaoSlaCobrancaSerializer(cfg, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)


class CobrarProtocoloSerializer(serializers.Serializer):
    mensagem = serializers.CharField(required=False, allow_blank=True, max_length=300)


class ProtocoloCobrarMixin:
    """Mixin para POST cobrar no viewset de protocolos."""

    def cobrar_protocolo(self, request, protocolo):
        from atendimentos.services.sla_cobranca_service import executar_cobranca_cidadao
        from rest_framework.exceptions import Throttled

        ser = CobrarProtocoloSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            cob = executar_cobranca_cidadao(
                protocolo,
                request.user,
                mensagem=ser.validated_data.get("mensagem") or "",
                request=request,
            )
        except Throttled as exc:
            raise exc
        return Response(
            {
                "id": str(cob.id),
                "protocolo": protocolo.codigo,
                "qtd_cobrancas_cidadao": protocolo.qtd_cobrancas_cidadao,
                "ultima_cobranca_em": cob.criado_em.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            status=status.HTTP_201_CREATED,
        )


def _parse_bool(val) -> bool | None:
    if val is None:
        return None
    return str(val).lower() in ("1", "true", "yes", "sim")


def _filtros_relatorio(request) -> dict:
    raw_unidade = request.query_params.get("unidade_id")
    raw_servico = request.query_params.get("servico_id")
    raw_equip = request.query_params.get("equipamento_id")
    dias_min = request.query_params.get("dias_atraso_min")
    return {
        "unidade_id": UUID(raw_unidade) if raw_unidade else None,
        "servico_id": UUID(raw_servico) if raw_servico else None,
        "equipamento_id": UUID(raw_equip) if raw_equip else None,
        "apenas_cobrados": _parse_bool(request.query_params.get("apenas_cobrados")),
        "dias_atraso_min": int(dias_min) if dias_min and str(dias_min).isdigit() else None,
        "ordenacao": request.query_params.get("ordenacao") or "atraso_desc",
    }


class RelatorioSlaAtrasadosView(APIView):
    permission_classes = [IsAuthenticated, PermissaoMesaTrabalho]

    def get(self, request):
        filtros = _filtros_relatorio(request)
        qs = filtrar_relatorio_atrasados(request.user, **filtros)
        resumo = resumo_relatorio_atrasados(qs)

        page = int(request.query_params.get("page") or 1)
        page_size = min(int(request.query_params.get("page_size") or 25), 100)
        start = (page - 1) * page_size
        slice_qs = qs[start : start + page_size]
        resultados = [serializar_item_relatorio(p) for p in slice_qs]

        return Response(
            {
                "resumo": resumo,
                "paginacao": {
                    "pagina": page,
                    "tamanho_pagina": page_size,
                    "total": qs.count(),
                },
                "resultados": resultados,
            }
        )


class RelatorioSlaAtrasadosExportarView(APIView):
    permission_classes = [IsAuthenticated, PermissaoMesaTrabalho]

    def get(self, request):
        filtros = _filtros_relatorio(request)
        qs = filtrar_relatorio_atrasados(request.user, **filtros)
        conteudo = exportar_csv_relatorio_atrasados(qs)
        resp = HttpResponse(conteudo, content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = 'attachment; filename="sla-atrasados.csv"'
        return resp


class RelatorioSlaDispararView(APIView):
    permission_classes = [IsAuthenticated, PermissaoMesaTrabalho]

    def post(self, request):
        unidade_raw = (request.data or {}).get("unidade_id")
        unidade_id = UUID(str(unidade_raw)) if unidade_raw else None
        incluir = (request.data or {}).get("incluir_controladoria", True)
        envios = enviar_digest_sla_atrasados(
            unidade_id=unidade_id,
            incluir_controladoria=bool(incluir),
            disparado_por=request.user,
        )
        return Response(
            {
                "envios": [
                    {
                        "id": str(e.id),
                        "tipo": e.tipo,
                        "status": e.status,
                        "destinatarios": e.destinatarios,
                        "total_protocolos": e.total_protocolos,
                        "total_cobrados": e.total_cobrados,
                    }
                    for e in envios
                ]
            },
            status=status.HTTP_202_ACCEPTED,
        )


class RelatorioSlaEnviosListView(APIView):
    permission_classes = [IsAuthenticated, PermissaoMesaTrabalho]

    def get(self, request):
        page = int(request.query_params.get("page") or 1)
        page_size = min(int(request.query_params.get("page_size") or 20), 50)
        start = (page - 1) * page_size
        qs = RelatorioSlaEnvio.objects.all().select_related("unidade", "disparado_por")
        total = qs.count()
        itens = []
        for e in qs[start : start + page_size]:
            itens.append(
                {
                    "id": str(e.id),
                    "tipo": e.tipo,
                    "unidade": e.unidade.nome if e.unidade_id else None,
                    "destinatarios": e.destinatarios,
                    "total_protocolos": e.total_protocolos,
                    "total_cobrados": e.total_cobrados,
                    "status": e.status,
                    "erro_detalhe": e.erro_detalhe or "",
                    "disparado_por": e.disparado_por.nome if e.disparado_por_id else None,
                    "criado_em": e.criado_em.strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            )
        return Response(
            {
                "paginacao": {"pagina": page, "tamanho_pagina": page_size, "total": total},
                "resultados": itens,
            }
        )


def campos_cobranca_protocolo_pwa(protocolo, user) -> dict:
    eleg = avaliar_elegibilidade_cobranca(protocolo, user)
    return {
        "pode_cobrar": eleg.pode,
        "motivo_bloqueio_cobranca": eleg.motivo,
        "proxima_cobranca_em": (
            eleg.proxima_cobranca_em.strftime("%Y-%m-%dT%H:%M:%SZ")
            if eleg.proxima_cobranca_em
            else None
        ),
        "qtd_cobrancas_cidadao": int(protocolo.qtd_cobrancas_cidadao or 0),
        "dias_atraso": dias_atraso(protocolo),
        "prazo_sla": prazo_sla_dt(protocolo).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ultimo_alerta_sla_nivel": protocolo.ultimo_alerta_sla_nivel or "",
    }