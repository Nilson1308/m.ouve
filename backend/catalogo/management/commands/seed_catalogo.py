"""Carga inicial do catálogo (espelha o mock do frontend Vue)."""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import ProtectedError

from catalogo.models import ServicoCatalogo
from catalogo.seed_data import popular_catalogo_inicial


class Command(BaseCommand):
    help = "Remove serviços existentes e cadastra os 6 serviços base do catálogo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-clear",
            action="store_true",
            help="Não apaga registros; apenas faz upsert pelos IDs estáveis.",
        )

    def handle(self, *args, **options):
        limpar = not options["no_clear"]

        if limpar:
            try:
                count, _ = ServicoCatalogo.objects.all().delete()
                if count:
                    self.stdout.write(f"Removidos {count} registro(s) do catálogo.")
            except ProtectedError as exc:
                protegidos = exc.protected_objects
                raise CommandError(
                    "Não foi possível limpar o catálogo: existem protocolos vinculados "
                    f"({len(protegidos)} serviço(s) protegido(s)). "
                    "Apague ou reassocie os protocolos, ou use --no-clear."
                ) from exc

        total = popular_catalogo_inicial(limpar=False)
        self.stdout.write(
            self.style.SUCCESS(f"Catálogo atualizado: {total} serviço(s) cadastrado(s).")
        )
