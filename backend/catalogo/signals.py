"""Invalidação de cache do PWA ao alterar o catálogo."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from catalogo.models import ServicoCatalogo
from catalogo.pwa_catalogo import invalidar_cache_config_pwa


@receiver(post_save, sender=ServicoCatalogo)
def servico_catalogo_invalida_config_pwa(sender, instance, **kwargs):
    invalidar_cache_config_pwa()