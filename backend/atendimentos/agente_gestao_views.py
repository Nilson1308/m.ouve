"""API — Agente IA proativo (Radar / briefing)."""

from __future__ import annotations

from django.shortcuts import get_object_or_404
from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import Throttled
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.models import AvaliacaoInsightIA, BriefingOperacionalIA, ConfiguracaoAgenteGestao
from atendimentos.configuracao_agente_gestao_serializers import ConfiguracaoAgenteGestaoSerializer
from atendimentos.services.agente_briefing_service import (
    gerar_briefing_escopo,
    marcar_forcar_usado,
    obter_consumo_tokens_mes,
    verificar_rate_limit_forcar,
)
from atendimentos.services.agente_persona import (
    resolver_escopo_briefing_usuario,
    usuario_pode_acessar_briefing,
)
from catalogo.models import UnidadeAdministrativa
from core_auth.permissions import IsBackofficeStaff
from core_auth.rbac import make_has_module_permission


class ConfiguracaoAgenteGestaoView(APIView):
    def get_permissions(self):
        acao = "editar" if self.request.method in ("PATCH", "PUT") else "ler"
        return [
            IsAuthenticated(),
            IsBackofficeStaff(),
            make_has_module_permission("configuracoes", acao)(),
        ]

    def get(self, request):
        return Response(ConfiguracaoAgenteGestaoSerializer(ConfiguracaoAgenteGestao.load()).data)

    def patch(self, request):
        cfg = ConfiguracaoAgenteGestao.load()
        ser = ConfiguracaoAgenteGestaoSerializer(cfg, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)


class BriefingAgenteGestaoView(APIView):
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request):
        escopo_tipo, unidade_id = resolver_escopo_briefing_usuario(
            request.user, request.query_params
        )
        unidade = None
        if escopo_tipo == "unidade" and unidade_id:
            unidade = get_object_or_404(UnidadeAdministrativa, pk=unidade_id, ativo=True)

        forcar = request.query_params.get("forcar", "").lower() in ("1", "true", "sim")
        if forcar:
            ok, ttl = verificar_rate_limit_forcar(escopo_tipo, unidade_id)
            if not ok:
                proxima = timezone.now() + timedelta(seconds=ttl or 900)
                raise Throttled(
                    detail={
                        "detail": "Atualização forçada limitada a 1 a cada 15 minutos.",
                        "proxima_atualizacao_em": proxima.isoformat(),
                    }
                )
            marcar_forcar_usado(escopo_tipo, unidade_id)

        briefing = gerar_briefing_escopo(escopo_tipo, unidade=unidade, forcar=forcar)
        cfg = ConfiguracaoAgenteGestao.load()
        consumo = obter_consumo_tokens_mes()
        orcamento = int(cfg.orcamento_tokens_mensal)
        pct = round(100.0 * consumo / orcamento, 2) if orcamento else 0

        avaliacoes = {
            a.insight_id: a.util
            for a in AvaliacaoInsightIA.objects.filter(
                briefing=briefing, usuario=request.user
            )
        }

        return Response(
            {
                "briefing_id": str(briefing.id),
                "escopo_tipo": briefing.escopo_tipo,
                "unidade_id": str(briefing.unidade_id) if briefing.unidade_id else None,
                "data_referencia": briefing.data_referencia.isoformat(),
                "modo_geracao": briefing.modo_geracao,
                "modelo_llm": briefing.modelo_llm,
                "fatos_deterministicos": briefing.fatos_deterministicos,
                "conteudo": briefing.conteudo_ia,
                "resumo_executivo_email": briefing.resumo_executivo_email,
                "tokens_mes_atual": consumo,
                "orcamento_tokens_mensal": orcamento,
                "percentual_consumo": pct,
                "minhas_avaliacoes": avaliacoes,
            }
        )


class AvaliarInsightBriefingView(APIView):
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def post(self, request, briefing_id):
        briefing = get_object_or_404(BriefingOperacionalIA, pk=briefing_id)
        if not usuario_pode_acessar_briefing(request.user, briefing):
            return Response(status=status.HTTP_403_FORBIDDEN)

        insight_id = (request.data.get("insight_id") or "").strip()[:64]
        if not insight_id:
            return Response(
                {"insight_id": ["Obrigatório."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        util = bool(request.data.get("util"))
        comentario = (request.data.get("comentario") or "").strip()[:300]

        obj, _created = AvaliacaoInsightIA.objects.update_or_create(
            briefing=briefing,
            insight_id=insight_id,
            usuario=request.user,
            defaults={"util": util, "comentario": comentario},
        )
        return Response(
            {
                "id": str(obj.id),
                "insight_id": obj.insight_id,
                "util": obj.util,
                "comentario": obj.comentario,
            }
        )