"""CRUD governança — catálogo de serviços (Form Builder)."""

from django.db.models import Count, Q
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from catalogo.governanca_serializers import (
    CategoriaCatalogoGovernancaSerializer,
    ServicoCatalogoClonarSerializer,
    ServicoCatalogoGovernancaSerializer,
    ServicoCatalogoPublicarSerializer,
    ServicoCatalogoSandboxSerializer,
    ServicoCatalogoVersaoSerializer,
)
from catalogo.sandbox_service import executar_sandbox_servico_catalogo
from catalogo.template_service import instanciar_servico_catalogo
from catalogo.models import CategoriaCatalogo, ServicoCatalogo, ServicoCatalogoVersao
from catalogo.versionamento_service import (
    descartar_rascunho,
    publicar_rascunho,
    restaurar_versao_para_rascunho,
)
from core_auth.permissions import PermissaoConfiguracoes

PodeGerirCatalogoServicos = PermissaoConfiguracoes


class ServicoCatalogoFilterSet(filters.FilterSet):
    ativo = filters.BooleanFilter(field_name="ativo")
    unidade_responsavel_id = filters.UUIDFilter(field_name="unidade_responsavel_id")
    categoria_id = filters.UUIDFilter(field_name="categoria_id")
    busca = filters.CharFilter(method="filter_busca")

    class Meta:
        model = ServicoCatalogo
        fields = ("ativo", "unidade_responsavel_id", "categoria_id")

    def filter_busca(self, queryset, name, value):
        termo = (value or "").strip()
        if not termo:
            return queryset
        return queryset.filter(Q(nome__icontains=termo) | Q(descricao__icontains=termo))


class CategoriaCatalogoGovernancaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PodeGerirCatalogoServicos]
    serializer_class = CategoriaCatalogoGovernancaSerializer
    pagination_class = None
    lookup_field = "pk"

    def get_queryset(self):
        return (
            CategoriaCatalogo.objects.annotate(servicos_count=Count("servicos"))
            .order_by("ordem", "nome")
        )

    def perform_destroy(self, instance):
        if instance.servicos.exists():
            instance.ativo = False
            instance.save(update_fields=["ativo", "atualizado_em"])
        else:
            instance.delete()


class ServicoCatalogoGovernancaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PodeGerirCatalogoServicos]
    serializer_class = ServicoCatalogoGovernancaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ServicoCatalogoFilterSet
    pagination_class = None
    lookup_field = "pk"

    def get_queryset(self):
        return (
            ServicoCatalogo.objects.filter(is_template=False)
            .select_related("categoria", "unidade_responsavel")
            .order_by("categoria__ordem", "nome")
        )

    def perform_destroy(self, instance):
        if instance.protocolos.exists():
            instance.ativo = False
            instance.save(update_fields=["ativo", "atualizado_em"])
        else:
            instance.delete()

    @action(detail=False, methods=["get"], url_path="templates")
    def templates(self, request):
        """Lista modelos globais clonáveis (is_template=True)."""
        qs = (
            ServicoCatalogo.objects.filter(is_template=True)
            .select_related("categoria", "unidade_responsavel")
            .order_by("categoria__ordem", "nome")
        )
        serializer = ServicoCatalogoGovernancaSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="clonar")
    def clonar(self, request, pk=None):
        """
        Template (is_template): novo serviço ativo na unidade informada.
        Serviço municipal: duplicata inativa com nome «… (Cópia)»; unidade opcional.
        """
        try:
            origem = ServicoCatalogo.objects.select_related(
                "categoria",
                "unidade_responsavel",
            ).get(pk=pk)
        except ServicoCatalogo.DoesNotExist:
            return Response(
                {"detail": "Serviço ou modelo não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ServicoCatalogoClonarSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        unidade = serializer.validated_data.get("unidade_responsavel")
        try:
            novo = instanciar_servico_catalogo(
                origem,
                unidade_responsavel=unidade,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        out = ServicoCatalogoGovernancaSerializer(novo)
        return Response(out.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="sandbox")
    def sandbox(self, request, pk=None):
        """
        Simula um turno do chat do serviço (dry-run).
        Não cria SessaoChat, Protocolo ou Atendimento.
        """
        servico = self.get_object()
        serializer = ServicoCatalogoSandboxSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        resultado = executar_sandbox_servico_catalogo(
            servico,
            mensagem=data.get("mensagem") or "",
            dados_parciais=data.get("dados_parciais"),
            dados_slot=data.get("dados_slot"),
            anexos_novos=data.get("anexos_novos") or 0,
            localizacao_ok=bool(data.get("localizacao_ok")),
            localizacao=data.get("localizacao"),
            historico=data.get("historico"),
            usar_rascunho=data.get("usar_rascunho"),
        )
        return Response(resultado, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="publicar")
    def publicar(self, request, pk=None):
        servico = self.get_object()
        ser = ServicoCatalogoPublicarSerializer(data=request.data or {})
        ser.is_valid(raise_exception=True)
        try:
            publicar_rascunho(
                servico,
                request.user,
                nota_versao=ser.validated_data.get("nota_versao") or "",
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        servico.refresh_from_db()
        out = ServicoCatalogoGovernancaSerializer(servico)
        return Response(out.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="descartar-rascunho")
    def descartar_rascunho_action(self, request, pk=None):
        servico = self.get_object()
        descartar_rascunho(servico)
        servico.refresh_from_db()
        out = ServicoCatalogoGovernancaSerializer(servico)
        return Response(out.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="versoes")
    def versoes(self, request, pk=None):
        servico = self.get_object()
        qs = ServicoCatalogoVersao.objects.filter(servico=servico).select_related(
            "publicado_por"
        )
        ser = ServicoCatalogoVersaoSerializer(qs, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path=r"versoes/(?P<numero_versao>[0-9]+)/restaurar",
    )
    def restaurar_versao(self, request, pk=None, numero_versao=None):
        servico = self.get_object()
        try:
            numero = int(numero_versao)
        except (TypeError, ValueError):
            return Response(
                {"detail": "Número de versão inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            restaurar_versao_para_rascunho(servico, numero)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        servico.refresh_from_db()
        out = ServicoCatalogoGovernancaSerializer(servico)
        return Response(out.data, status=status.HTTP_200_OK)