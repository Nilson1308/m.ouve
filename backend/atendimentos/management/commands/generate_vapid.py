"""Gera par de chaves VAPID (Web Push) para o PWA."""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from atendimentos.vapid_keys import generate_vapid_keypair


class Command(BaseCommand):
    help = (
        "Gera private_key.pem e public_key.pem (VAPID) e imprime valores para o .env. "
        "A chave privada nunca deve ser commitada."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            "-o",
            default=".",
            help="Diretório de saída (padrão: diretório atual)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Sobrescreve PEMs existentes",
        )
        parser.add_argument(
            "--email",
            default="",
            help="Sugestão para VAPID_ADMIN_EMAIL (ex.: mailto:ouvidoria@municipio.gov.br)",
        )

    def handle(self, *args, **options):
        output_dir = Path(options["output_dir"]).resolve()
        try:
            private_path, public_path, app_key = generate_vapid_keypair(
                output_dir, force=options["force"]
            )
        except FileExistsError as exc:
            raise CommandError(str(exc)) from exc

        email = (options["email"] or getattr(settings, "VAPID_ADMIN_EMAIL", "") or "").strip()
        if not email:
            email = "mailto:ouvidoria@example.gov.br"

        self.stdout.write(self.style.SUCCESS("Chaves VAPID geradas com sucesso."))
        self.stdout.write(f"  Privada: {private_path}")
        self.stdout.write(f"  Pública (PEM): {public_path}")
        self.stdout.write("")
        self.stdout.write("Adicione ao backend/.env (e ao ambiente do worker Celery):")
        self.stdout.write("")
        self.stdout.write(f"VAPID_PUBLIC_KEY={app_key}")
        self.stdout.write(f"VAPID_PRIVATE_KEY={private_path}")
        self.stdout.write(f"VAPID_ADMIN_EMAIL={email}")
        self.stdout.write("")
        self.stdout.write(
            "No PWA, use GET /api/v1/app/notificacoes/vapid-public-key "
            "ou a mesma VAPID_PUBLIC_KEY no applicationServerKey."
        )