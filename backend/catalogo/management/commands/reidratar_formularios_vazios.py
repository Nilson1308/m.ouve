"""Reidrata serviços municipais sem formulário (Iluminação Pública, Limpeza Urbana, etc.)."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from catalogo.models import ServicoCatalogo
from catalogo.reidratar_service import (
    reidratar_servico_formulario,
    servico_formulario_vazio,
)
from catalogo.reidratar_service import _REIDRATAR_POR_NOME


class Command(BaseCommand):
    help = (
        "Copia formulário de template da biblioteca ou do seed para serviços municipais vazios. "
        "Use --publicar para promover rascunho (ou só --persist para deixar em rascunho)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--persist",
            action="store_true",
            help="Grava rascunho (ou publica com --publicar).",
        )
        parser.add_argument(
            "--publicar",
            action="store_true",
            help="Publica após reidratar (requer --persist).",
        )
        parser.add_argument("--servico-id", type=str, default="")

    def handle(self, *args, **options):
        persist = options["persist"]
        publicar = options["publicar"]
        servico_id = (options["servico_id"] or "").strip()

        if publicar and not persist:
            self.stderr.write(self.style.ERROR("--publicar exige --persist."))
            return

        qs = ServicoCatalogo.objects.filter(is_template=False)
        if servico_id:
            qs = qs.filter(pk=servico_id)

        user = get_user_model().objects.filter(is_superuser=True).order_by("pk").first()

        ok = 0
        pulados = 0
        erros = 0

        for servico in qs.order_by("nome"):
            nome = (servico.nome or "").strip()
            if nome not in _REIDRATAR_POR_NOME:
                continue
            if not servico_formulario_vazio(servico):
                pulados += 1
                continue
            if not persist:
                self.stdout.write(f"↷ {nome}: reidrataría de {_REIDRATAR_POR_NOME[nome][1]}")
                ok += 1
                continue
            try:
                reidratar_servico_formulario(servico, publicar=publicar, user=user)
                modo = "publicado" if publicar else "rascunho"
                self.stdout.write(self.style.SUCCESS(f"✓ {nome}: {modo}"))
                ok += 1
            except ValueError as exc:
                self.stdout.write(self.style.ERROR(f"✗ {nome}: {exc}"))
                erros += 1

        self.stdout.write(
            self.style.SUCCESS(f"Concluído: {ok} processados, {pulados} já preenchidos, {erros} erros.")
        )