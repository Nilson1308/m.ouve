"""ViewSets de governança — unidades administrativas e usuários (Sprint 4)."""

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from catalogo.models import UnidadeAdministrativa
from core_auth.governanca_serializers import (
    PerfilAcessoSerializer,
    ResetarSenhaResponseSerializer,
    UnidadeAdministrativaGovernancaSerializer,
    UsuarioGovernancaCreateSerializer,
    UsuarioGovernancaSerializer,
    gerar_senha_aleatoria,
)
from core_auth.models import PerfilAcesso, Usuario
from core_auth.permissions import IsSuperAdmin, PermissaoConfiguracoes, PermissaoGestaoUsuarios


def _termo_busca_filterset(filterset, value) -> str:
    termo = (value or "").strip()
    if termo:
        return termo
    request = getattr(filterset, "request", None)
    if not request:
        return ""
    params = getattr(request, "query_params", None) or getattr(request, "GET", {})
    return (params.get("busca") or params.get("search") or "").strip()


class UnidadeAdministrativaFilterSet(filters.FilterSet):
    ativo = filters.BooleanFilter(field_name="ativo")
    busca = filters.CharFilter(method="filter_busca")
    search = filters.CharFilter(method="filter_busca")

    class Meta:
        model = UnidadeAdministrativa
        fields = ("ativo",)

    def filter_busca(self, queryset, name, value):
        termo = _termo_busca_filterset(self, value)
        if not termo:
            return queryset
        return queryset.filter(
            Q(nome__icontains=termo)
            | Q(sigla__icontains=termo)
            | Q(descricao__icontains=termo)
        )


class UnidadeAdministrativaGovernancaViewSet(viewsets.ModelViewSet):
    """CRUD de unidades — somente Super Admin."""

    permission_classes = [IsAuthenticated, PermissaoConfiguracoes]
    serializer_class = UnidadeAdministrativaGovernancaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UnidadeAdministrativaFilterSet
    pagination_class = None
    lookup_field = "pk"

    def get_queryset(self):
        return UnidadeAdministrativa.objects.annotate(
            qtd_usuarios=Count(
                "servidores",
                filter=Q(servidores__is_active=True),
            )
        ).order_by("nome")

    def perform_destroy(self, instance):
        vinculados = instance.servidores.filter(is_active=True, perfil_acesso__isnull=False).count()
        if vinculados:
            instance.ativo = False
            instance.save(update_fields=["ativo", "atualizado_em"])
        else:
            instance.delete()


class PerfilAcessoFilterSet(filters.FilterSet):
    busca = filters.CharFilter(method="filter_busca")

    class Meta:
        model = PerfilAcesso
        fields = ()

    def filter_busca(self, queryset, name, value):
        termo = (value or "").strip()
        if not termo:
            return queryset
        return queryset.filter(
            Q(nome__icontains=termo) | Q(codigo__icontains=termo)
        )


class PerfilAcessoGovernancaViewSet(viewsets.ModelViewSet):
    """CRUD de perfis de acesso — somente Super Admin."""

    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = PerfilAcessoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PerfilAcessoFilterSet
    pagination_class = None
    lookup_field = "pk"

    def get_queryset(self):
        return (
            PerfilAcesso.objects.annotate(
                qtd_usuarios=Count("usuarios", filter=Q(usuarios__is_active=True))
            ).order_by("nome")
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.sistema:
            return Response(
                {"detail": "Perfis de sistema não podem ser excluídos. Edite as permissões."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if instance.usuarios.filter(is_active=True).exists():
            return Response(
                {"detail": "Há usuários ativos com este perfil. Reatribua antes de excluir."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UsuarioGovernancaFilterSet(filters.FilterSet):
    perfil = filters.CharFilter(method="filter_perfil")
    perfil_acesso_id = filters.UUIDFilter(field_name="perfil_acesso_id")
    unidade_id = filters.UUIDFilter(field_name="unidade_id")
    busca = filters.CharFilter(method="filter_busca")
    search = filters.CharFilter(method="filter_busca")

    class Meta:
        model = Usuario
        fields = ("perfil_acesso_id", "unidade_id")

    def filter_perfil(self, queryset, name, value):
        codigo = (value or "").strip().lower()
        if not codigo:
            return queryset
        return queryset.filter(perfil_acesso__codigo=codigo)

    def filter_busca(self, queryset, name, value):
        termo = _termo_busca_filterset(self, value)
        if not termo:
            return queryset
        return queryset.filter(
            Q(nome__icontains=termo)
            | Q(email__icontains=termo)
            | Q(perfil_acesso__nome__icontains=termo)
            | Q(perfil_acesso__codigo__icontains=termo)
            | Q(unidade__nome__icontains=termo)
            | Q(unidade__sigla__icontains=termo)
        )


class UsuarioGovernancaViewSet(viewsets.ModelViewSet):
    """CRUD de usuários internos — permissão `gestao_usuarios`."""

    permission_classes = [IsAuthenticated, PermissaoGestaoUsuarios]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UsuarioGovernancaFilterSet
    pagination_class = None
    lookup_field = "pk"

    def get_queryset(self):
        return (
            Usuario.objects.filter(perfil_acesso__isnull=False)
            .select_related("unidade", "perfil_acesso")
            .order_by("nome")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return UsuarioGovernancaCreateSerializer
        return UsuarioGovernancaSerializer

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])

    @action(detail=True, methods=["post"], url_path="resetar-senha")
    def resetar_senha(self, request, pk=None):
        usuario = get_object_or_404(self.get_queryset(), pk=pk)
        senha = gerar_senha_aleatoria()
        usuario.set_password(senha)
        usuario.save(update_fields=["password", "updated_at"])
        payload = {
            "sucesso": True,
            "mensagem": "Senha redefinida. Entregue a senha temporária ao servidor.",
            "usuario_id": usuario.id,
            "senha": senha,
            "email": usuario.email,
        }
        serializer = ResetarSenhaResponseSerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)