"""Audita e corrige protocolos com geo/bairro herdados indevidamente do EnderecoCidadao."""

from django.core.management.base import BaseCommand

from atendimentos.models import Protocolo
from atendimentos.services.protocolo_geolocalizacao import (
    limpar_contaminacao_residencial,
    protocolo_contaminado_residencia,
)


class Command(BaseCommand):
    help = "Remove coordenadas/bairros residenciais indevidos de protocolos de Ouvidoria."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Apenas lista protocolos afetados sem gravar.",
        )

    def handle(self, *args, **options):
        dry = options["dry_run"]
        qs = Protocolo.objects.select_related("usuario", "usuario__endereco", "servico")
        afetados = 0
        corrigidos = 0
        for protocolo in qs.iterator(chunk_size=200):
            if not protocolo_contaminado_residencia(protocolo):
                continue
            afetados += 1
            self.stdout.write(
                f"  {protocolo.codigo} · origem={protocolo.origem_localizacao} · "
                f"geo={'sim' if protocolo.localizacao else 'não'}"
            )
            if dry:
                continue
            campos = limpar_contaminacao_residencial(protocolo)
            if campos:
                protocolo.save(update_fields=list(dict.fromkeys(campos + ["data_atualizacao"])))
                corrigidos += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Auditados: {qs.count()} | contaminados: {afetados} | "
                f"{'(dry-run)' if dry else f'corrigidos: {corrigidos}'}"
            )
        )