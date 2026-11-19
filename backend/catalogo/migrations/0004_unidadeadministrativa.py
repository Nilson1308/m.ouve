import uuid

from django.db import migrations, models


def seed_unidades(apps, schema_editor):
    Unidade = apps.get_model("catalogo", "UnidadeAdministrativa")
    defaults = [
        ("Secretaria de Obras Públicas", "SOP"),
        ("Obras — Equipe de Pavimentação", "SOP-PAV"),
        ("Defesa Civil", "DC"),
        ("Departamento de Trânsito", "DTRAN"),
        ("Iluminação Pública", "ILUM"),
        ("Secretaria de Limpeza Urbana", "SLU"),
        ("Secretaria do Meio Ambiente", "SMA"),
        ("Vigilância Sanitária", "VISA"),
        ("Zeladoria Urbana", "ZEL"),
    ]
    for nome, sigla in defaults:
        Unidade.objects.get_or_create(
            sigla=sigla,
            defaults={"id": uuid.uuid4(), "nome": nome, "ativa": True},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("catalogo", "0003_categoria_catalogo"),
    ]

    operations = [
        migrations.CreateModel(
            name="UnidadeAdministrativa",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("nome", models.CharField(max_length=255)),
                ("sigla", models.CharField(blank=True, max_length=20)),
                ("ativa", models.BooleanField(default=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "unidade administrativa",
                "verbose_name_plural": "unidades administrativas",
                "ordering": ["nome"],
                "indexes": [
                    models.Index(fields=["ativa"], name="catalogo_un_ativa_idx")
                ],
            },
        ),
        migrations.RunPython(seed_unidades, migrations.RunPython.noop),
    ]
