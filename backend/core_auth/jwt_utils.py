"""Respostas JWT no formato esperado pelo frontend Vue."""

from rest_framework_simplejwt.tokens import RefreshToken

from core_auth.serializers import UsuarioResponseSerializer


def build_auth_response(user):
    """Monta `{ user, token, refresh_token }`."""
    refresh = RefreshToken.for_user(user)
    return {
        "user": UsuarioResponseSerializer(user).data,
        "token": str(refresh.access_token),
        "refresh_token": str(refresh),
    }
