"""Backfill de ``dados_dinamicos.bairro`` a partir de endereço/geo existentes."""

from django.core.management.base import BaseCommand

from atendimentos.models import Protocolo
from atendimentos.services.protocolo_localidade import (
    bairro_de_dados_dinamicos,
    sincronizar_localidade_protocolo,
)


class Command(BaseCommand):
    help = "Sincroniza bairro/cidade em dados_dinamicos dos protocolos (GIS e Mesa)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Apenas contabiliza alterações sem gravar.",
        )

    def handle(self, *args, **options):
        dry = options["dry_run"]
        qs = Protocolo.objects.select_related("usuario", "usuario__endereco")
        total = qs.count()
        alterados = 0
        ja_ok = 0

        for protocolo in qs.iterator(chunk_size=200):
            if bairro_de_dados_dinamicos(protocolo.dados_dinamicos):
                ja_ok += 1
                continue
            if dry:
                copia = Protocolo(
                    pk=protocolo.pk,
                    dados_dinamicos=dict(protocolo.dados_dinamicos or {}),
                    endereco_texto=protocolo.endereco_texto,
                    localizacao=protocolo.localizacao,
                    usuario=protocolo.usuario,
                )
                if sincronizar_localidade_protocolo(copia, persistir=False):
                    alterados += 1
                continue
            if sincronizar_localidade_protocolo(protocolo, persistir=True):
                alterados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Protocolos: {total} | já com bairro: {ja_ok} | "
                f"{'seriam atualizados' if dry else 'atualizados'}: {alterados}"
            )
        )