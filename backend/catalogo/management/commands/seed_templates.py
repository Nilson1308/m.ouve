"""Cria ou atualiza modelos globais (is_template=True) da biblioteca M.Ouve."""

from django.core.management.base import BaseCommand
from catalogo.models import CategoriaCatalogo, ServicoCatalogo
from catalogo.templates_seed_data import definicoes_templates


CATEGORIAS_EXTRA = [
    {
        "nome": "Saúde",
        "slug": "saude",
        "descricao": "Vigilância epidemiológica, zoonoses e protocolos de saúde pública.",
        "icone": "heart",
        "ordem": 30,
        "ativo": True,
    },
]


class Command(BaseCommand):
    help = "Seed da biblioteca de templates clonáveis (ServicoCatalogo.is_template=True)."

    def handle(self, *args, **options):
        for cat in CATEGORIAS_EXTRA:
            CategoriaCatalogo.objects.update_or_create(
                slug=cat["slug"],
                defaults={
                    "nome": cat["nome"],
                    "descricao": cat["descricao"],
                    "icone": cat["icone"],
                    "ordem": cat["ordem"],
                    "ativo": cat["ativo"],
                },
            )

        criados = 0
        atualizados = 0
        for item in definicoes_templates():
            slug = item["categoria_slug"]
            categoria = CategoriaCatalogo.objects.filter(slug=slug).first()
            if not categoria:
                categoria = CategoriaCatalogo.objects.create(
                    nome=slug.replace("_", " ").title(),
                    slug=slug,
                    ativo=True,
                    ordem=50,
                    icone="squares-2x2",
                )
                self.stdout.write(self.style.WARNING(f"Categoria criada: {categoria.slug}"))

            defaults = {
                "categoria": categoria,
                "nome": item["nome"],
                "descricao": item["descricao"],
                "icone": item["icone"],
                "sla_horas": item["sla_horas"],
                "formulario_schema": item["formulario_schema"],
                "schema_formulario": item["schema_formulario"],
                "ativo": True,
                "is_template": True,
                "unidade_responsavel": None,
            }
            _, created = ServicoCatalogo.objects.update_or_create(
                id=item["id"],
                defaults=defaults,
            )
            if created:
                criados += 1
            else:
                atualizados += 1
            self.stdout.write(
                f"{'✓ novo' if created else '↻ atualizado'}: {item['nome']} ({item['id']})"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Biblioteca de templates: {criados} criado(s), {atualizados} atualizado(s)."
            )
        )