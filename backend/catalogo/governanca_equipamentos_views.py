"""CRUD governança — equipamentos públicos."""

from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from catalogo.equipamento_utils import filtrar_equipamentos_busca
from catalogo.governanca_equipamentos_serializers import EquipamentoPublicoSerializer
from catalogo.models import EquipamentoPublico
from core_auth.permissions import PermissaoConfiguracoes


class EquipamentoPublicoFilterSet(filters.FilterSet):
    busca = filters.CharFilter(method="filter_busca")
    unidade_id = filters.UUIDFilter(field_name="unidade_responsavel_id")
    tipo = filters.CharFilter(field_name="tipo")
    ativo = filters.BooleanFilter(field_name="ativo")

    class Meta:
        model = EquipamentoPublico
        fields = ("unidade_id", "tipo", "ativo")

    def filter_busca(self, queryset, name, value):
        return filtrar_equipamentos_busca(queryset, value)


class EquipamentoPublicoGovernancaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermissaoConfiguracoes]
    serializer_class = EquipamentoPublicoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = EquipamentoPublicoFilterSet
    lookup_field = "pk"
    pagination_class = None

    def get_queryset(self):
        return (
            EquipamentoPublico.objects.select_related("unidade_responsavel")
            .order_by("nome")
        )