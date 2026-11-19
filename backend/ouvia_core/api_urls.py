"""Rotas da API v1 — composição dos apps modulares."""

from django.urls import include, path

urlpatterns = [
    path("", include("core_auth.urls")),
    path("", include("catalogo.urls")),
    path("", include("atendimentos.urls")),
]
