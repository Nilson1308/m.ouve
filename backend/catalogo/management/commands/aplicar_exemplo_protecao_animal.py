"""Aplica o exemplo documentado de elegibilidade — Castração / Proteção Animal."""

from django.core.management.base import BaseCommand, CommandError

from catalogo.exemplos.protecao_animal_castracao import (
    NOME_SERVICO_ALVO,
    formulario_schema_exemplo,
    schema_formulario_exemplo,
)
from catalogo.form_builder import normalizar_formulario_schema
from catalogo.models import ServicoCatalogo


class Command(BaseCommand):
    help = (
        "Atualiza o serviço de castração com regras de elegibilidade por campo "
        "e por protocolo (idade + doença), conforme API_CONTRACT.md."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--nome",
            default=NOME_SERVICO_ALVO,
            help="Nome exato do serviço no catálogo (default: castração).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Apenas mostra o que seria gravado, sem salvar.",
        )

    def handle(self, *args, **options):
        nome = (options["nome"] or "").strip()
        servico = ServicoCatalogo.objects.filter(nome=nome).first()
        if not servico:
            raise CommandError(f"Serviço não encontrado: {nome!r}")

        formulario = normalizar_formulario_schema(formulario_schema_exemplo())
        schema = schema_formulario_exemplo()

        self.stdout.write(f"Serviço: {servico.nome} ({servico.id})")
        self.stdout.write(
            f"Regras: {len(schema['$metadata']['regras_elegibilidade'])} "
            "(2 por campo + 1 protocolo)"
        )

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry-run — nada foi salvo."))
            return

        servico.formulario_schema = formulario
        servico.schema_formulario = schema
        servico.save(update_fields=["formulario_schema", "schema_formulario", "atualizado_em"])
        self.stdout.write(self.style.SUCCESS("Exemplo aplicado com sucesso."))