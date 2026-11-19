# Generated for ServicoCatalogo

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ServicoCatalogo",
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
                ("nome", models.CharField(max_length=200)),
                ("descricao", models.TextField(blank=True)),
                ("categoria", models.CharField(max_length=80)),
                ("sla_horas", models.PositiveIntegerField(default=72)),
                ("schema_formulario", models.JSONField(default=dict)),
                ("ativo", models.BooleanField(default=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "serviço do catálogo",
                "verbose_name_plural": "serviços do catálogo",
                "ordering": ["categoria", "nome"],
                "indexes": [
                    models.Index(
                        fields=["ativo", "categoria"],
                        name="catalogo_se_ativo_c_7b3e84_idx",
                    )
                ],
            },
        ),
    ]
