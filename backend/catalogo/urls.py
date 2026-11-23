from django.urls import include, path
from rest_framework.routers import DefaultRouter

from catalogo.governanca_views import (
    CategoriaCatalogoGovernancaViewSet,
    ServicoCatalogoGovernancaViewSet,
)
from catalogo.governanca_roteamento_views import (
    MatrizRoteamentoDetailView,
    MatrizRoteamentoListCreateView,
)
from catalogo.lookup_views import CatalogoLookupUnidadesView
from catalogo.views import CategoriaCatalogoListView, ServicoCatalogoListView

governanca_router = DefaultRouter(trailing_slash=False)
governanca_router.register(
    "backoffice/servicos-catalogo",
    ServicoCatalogoGovernancaViewSet,
    basename="governanca-servicos-catalogo",
)
governanca_router.register(
    "backoffice/categorias-catalogo",
    CategoriaCatalogoGovernancaViewSet,
    basename="governanca-categorias-catalogo",
)

urlpatterns = [
    path(
        "backoffice/catalogo/servicos/<uuid:servico_id>/roteamento",
        MatrizRoteamentoListCreateView.as_view(),
    ),
    path(
        "backoffice/catalogo/servicos/<uuid:servico_id>/roteamento/",
        MatrizRoteamentoListCreateView.as_view(),
    ),
    path(
        "backoffice/catalogo/servicos/<uuid:servico_id>/roteamento/<uuid:regra_id>",
        MatrizRoteamentoDetailView.as_view(),
    ),
    path(
        "backoffice/catalogo/servicos/<uuid:servico_id>/roteamento/<uuid:regra_id>/",
        MatrizRoteamentoDetailView.as_view(),
    ),
    path("catalogo-categorias", CategoriaCatalogoListView.as_view()),
    path("catalogo-servicos", ServicoCatalogoListView.as_view()),
    path("catalogo/lookup/unidades", CatalogoLookupUnidadesView.as_view()),
    path("catalogo/lookup/unidades/", CatalogoLookupUnidadesView.as_view()),
    path("", include(governanca_router.urls)),
]
