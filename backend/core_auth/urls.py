from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core_auth import views
from core_auth.governanca_views import (
    PerfilAcessoGovernancaViewSet,
    UnidadeAdministrativaGovernancaViewSet,
    UsuarioGovernancaViewSet,
)

governanca_router = DefaultRouter(trailing_slash=False)
governanca_router.register(
    "backoffice/unidades",
    UnidadeAdministrativaGovernancaViewSet,
    basename="governanca-unidades",
)
governanca_router.register(
    "backoffice/usuarios",
    UsuarioGovernancaViewSet,
    basename="governanca-usuarios",
)
governanca_router.register(
    "backoffice/perfis-acesso",
    PerfilAcessoGovernancaViewSet,
    basename="governanca-perfis-acesso",
)

urlpatterns = [
    path("auth/register", views.RegisterView.as_view()),
    path("auth/login", views.LoginView.as_view()),
    path("auth/logout", views.LogoutView.as_view()),
    path("auth/refresh", views.RefreshTokenView.as_view()),
    path("auth/govbr/authorize", views.GovBrAuthorizeView.as_view()),
    path("auth/govbr/callback", views.GovBrCallbackView.as_view()),
    path("auth/sso-municipal/callback", views.SsoMunicipalCallbackView.as_view()),
    path("auth/cpf/verificar", views.VerificarCpfView.as_view()),
    path("auth/recuperar-senha/solicitar", views.SolicitarRecuperacaoSenhaView.as_view()),
    path("auth/recuperar-senha/redefinir", views.RedefinirSenhaRecuperacaoView.as_view()),
    path("notificacoes", views.NotificacaoListView.as_view()),
    path("notificacoes/<uuid:pk>/ler", views.NotificacaoMarcarLidaView.as_view()),
    path("notificacoes/registro-push", views.RegistrarPushView.as_view()),
    path("usuario/me", views.UsuarioMeView.as_view()),
    path("usuario/me/", views.UsuarioMeView.as_view()),
    path("usuario/alterar-senha", views.AlterarSenhaView.as_view()),
    path("auth/me", views.UsuarioMeView.as_view()),
    path("auth/me/", views.UsuarioMeView.as_view()),
    path("auth/me/alterar-senha", views.AlterarSenhaView.as_view()),
    path("auth/me/alterar-senha/", views.AlterarSenhaView.as_view()),
    path("usuario/anonimizar", views.AnonimizarUsuarioView.as_view()),
    path("usuario/desativar", views.DesativarUsuarioView.as_view()),
    path("", include(governanca_router.urls)),
]
