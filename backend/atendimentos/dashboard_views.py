"""API Backoffice — dashboards analíticos (Sprint 5)."""

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.services.analytics_service import dashboard_eficiencia, dashboard_qualidade
from atendimentos.services.inelegibilidade_dashboard_service import dashboard_inelegibilidade
from atendimentos.services.dashboard_filters import listar_bairros_dashboard
from atendimentos.services.mapa_calor_service import mapa_calor_pontos
from core_auth.permissions import PermissaoMapaIA, PermissaoMesaTrabalho


class DashboardEficienciaView(APIView):
    """
    GET — TMA, funil de status e ranking de SLA por secretaria.
    Escopo filtrado por RBAC (município vs unidade do gestor).
    """

    permission_classes = [IsAuthenticated, PermissaoMesaTrabalho]

    def get(self, request):
        data = dashboard_eficiencia(request.user, request.query_params)
        return Response(data)


class DashboardMapaCalorView(APIView):
    """
    GET — coordenadas [lat, lng] para heatmap (Leaflet), sem paginação ORM pesada.
    Filtros macro via query string; escopo RBAC igual ao dashboard de eficiência.
    """

    permission_classes = [IsAuthenticated, PermissaoMapaIA]

    def get(self, request):
        data = mapa_calor_pontos(request.user, request.query_params)
        return Response(data)


class DashboardBairrosView(APIView):
    """GET — bairros distintos com protocolos no escopo RBAC (lista para filtros GIS)."""

    permission_classes = [IsAuthenticated, PermissaoMapaIA]

    def get(self, request):
        bairros = listar_bairros_dashboard(request.user)
        return Response({"bairros": bairros, "total": len(bairros)})


class DashboardInelegibilidadeView(APIView):
    """
    GET — sessões bloqueadas por regras de elegibilidade (escudo político / economia IA).
    """

    permission_classes = [IsAuthenticated, PermissaoMesaTrabalho]

    def get(self, request):
        data = dashboard_inelegibilidade(request.user, request.query_params)
        return Response(data)


class DashboardQualidadeView(APIView):
    """
    GET — Matriz de Qualidade Executiva (SLA cumprido × satisfação do cidadão)
    por unidade responsável do catálogo.
    """

    permission_classes = [IsAuthenticated, PermissaoMesaTrabalho]

    def get(self, request):
        data = dashboard_qualidade(request.user, request.query_params)
        return Response(data)