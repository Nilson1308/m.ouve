"""Utilitários do catálogo."""

from catalogo.models import CategoriaCatalogo, ServicoCatalogo
from catalogo.seed_data import popular_catalogo_inicial


def garantir_catalogo_padrao() -> None:
    """Garante categorias e serviços base quando o catálogo está vazio."""
    if not CategoriaCatalogo.objects.exists() or not ServicoCatalogo.objects.exists():
        popular_catalogo_inicial(limpar=False)
