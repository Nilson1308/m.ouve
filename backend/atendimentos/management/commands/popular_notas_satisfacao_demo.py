"""Preenche nota_satisfacao (1–5) em protocolos RESOLVIDO sem nota — apenas desenvolvimento/demo."""

import random

from django.core.management.base import BaseCommand

from atendimentos.models import AvaliacaoProtocolo, Protocolo


class Command(BaseCommand):
    help = (
        "Atribui notas aleatórias de satisfação a protocolos resolvidos sem nota "
        "(e espelha a última AvaliacaoProtocolo, se existir)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Apenas conta quantos registros seriam atualizados.",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="Seed do random para reprodutibilidade.",
        )

    def handle(self, *args, **options):
        if options.get("seed") is not None:
            random.seed(options["seed"])

        qs = Protocolo.objects.filter(
            status=Protocolo.Status.RESOLVIDO,
            nota_satisfacao__isnull=True,
        )
        total = qs.count()
        if options["dry_run"]:
            self.stdout.write(f"Protocolos a atualizar: {total}")
            return

        atualizados = 0
        for protocolo in qs.iterator(chunk_size=200):
            ultima = (
                AvaliacaoProtocolo.objects.filter(protocolo=protocolo)
                .order_by("-criado_em")
                .first()
            )
            if ultima:
                nota = ultima.nota
                comentario = (ultima.comentario or "").strip() or None
            else:
                nota = random.randint(1, 5)
                comentario = None

            protocolo.nota_satisfacao = nota
            protocolo.comentario_satisfacao = comentario
            protocolo.save(update_fields=["nota_satisfacao", "comentario_satisfacao"])
            atualizados += 1

        self.stdout.write(
            self.style.SUCCESS(f"Notas de satisfação atualizadas em {atualizados} protocolo(s).")
        )