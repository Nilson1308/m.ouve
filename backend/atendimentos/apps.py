from django.apps import AppConfig


class AtendimentosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "atendimentos"
    verbose_name = "Atendimentos"

    def ready(self):
        from atendimentos import signals  # noqa: F401
