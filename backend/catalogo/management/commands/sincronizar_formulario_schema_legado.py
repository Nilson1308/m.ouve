"""Reidrata formulario_schema a partir de schema_formulario (serviços legados ou dessincronizados)."""

from django.core.management.base import BaseCommand

from catalogo.formulario_resolution import formulario_schema_para_edicao
from catalogo.models import ServicoCatalogo


class Command(BaseCommand):
    help = (
        "Copia campos de schema_formulario → formulario_schema quando a lista do Form Builder "
        "estiver vazia. Use --persist para gravar no banco."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--persist",
            action="store_true",
            help="Grava formulario_schema publicado (não altera rascunhos).",
        )
        parser.add_argument(
            "--servico-id",
            type=str,
            default="",
            help="UUID de um serviço (opcional).",
        )

    def handle(self, *args, **options):
        persist = options["persist"]
        servico_id = (options["servico_id"] or "").strip()

        qs = ServicoCatalogo.objects.filter(is_template=False).select_related("categoria")
        if servico_id:
            qs = qs.filter(pk=servico_id)

        atualizados = 0
        ignorados = 0
        vazios = 0

        for servico in qs.order_by("nome"):
            lista, importado = formulario_schema_para_edicao(
                formulario=servico.formulario_schema,
                schema_formulario=servico.schema_formulario,
            )
            if not importado:
                if not (servico.formulario_schema or []) and not (
                    (servico.schema_formulario or {}).get("properties")
                ):
                    vazios += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"— {servico.nome}: sem schema publicado (reconstruir no Form Builder ou clonar modelo)"
                        )
                    )
                else:
                    ignorados += 1
                continue

            self.stdout.write(
                f"{'✓' if persist else '↷'} {servico.nome}: {len(lista)} campo(s) importados do JSON Schema"
            )
            if persist:
                servico.formulario_schema = lista
                servico.save(update_fields=["formulario_schema", "atualizado_em"])
                atualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Concluído: {atualizados} gravados, {ignorados} já OK, {vazios} sem dados para importar."
            )
        )