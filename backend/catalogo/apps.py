from django.apps import AppConfig


class CatalogoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalogo"
    verbose_name = "Catálogo de serviços"

    def ready(self):
        from catalogo import signals  # noqa: F401
