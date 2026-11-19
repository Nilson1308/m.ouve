# Generated manually for scatter-gather evidências e status aguardando_revisao

import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("atendimentos", "0007_ordemservico_unidade"),
    ]

    operations = [
        migrations.AddField(
            model_name="protocolo",
            name="observacoes_internas",
            field=models.TextField(
                blank=True,
                help_text="Notas internas do gestor (não expostas ao cidadão).",
            ),
        ),
        migrations.AddField(
            model_name="protocolo",
            name="resposta_cidadao",
            field=models.TextField(
                blank=True,
                help_text="Texto enviado ao cidadão na validação final do protocolo.",
            ),
        ),
        migrations.AlterField(
            model_name="protocolo",
            name="status",
            field=models.CharField(
                choices=[
                    ("em_analise", "Em análise"),
                    ("em_andamento", "Em andamento"),
                    ("aguardando_revisao", "Aguardando revisão"),
                    ("resolvido", "Resolvido"),
                    ("rejeitado", "Rejeitado"),
                ],
                default="em_analise",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="protocolohistorico",
            name="status",
            field=models.CharField(
                choices=[
                    ("em_analise", "Em análise"),
                    ("em_andamento", "Em andamento"),
                    ("aguardando_revisao", "Aguardando revisão"),
                    ("resolvido", "Resolvido"),
                    ("rejeitado", "Rejeitado"),
                ],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="ordemservico",
            name="concluido_em",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="ordemservico",
            name="observacoes_execucao",
            field=models.TextField(blank=True),
        ),
        migrations.CreateModel(
            name="AnexoOrdemServico",
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
                ("arquivo", models.FileField(upload_to="ordens/anexos/%Y/%m/")),
                ("tipo_mime", models.CharField(blank=True, max_length=120)),
                ("nome_original", models.CharField(blank=True, max_length=255)),
                (
                    "tipo_evidencia",
                    models.CharField(
                        choices=[
                            ("antes", "Antes"),
                            ("depois", "Depois"),
                            ("durante", "Durante"),
                            ("outro", "Outro"),
                        ],
                        default="depois",
                        max_length=16,
                    ),
                ),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                (
                    "ordem",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="anexos",
                        to="atendimentos.ordemservico",
                    ),
                ),
            ],
            options={
                "verbose_name": "anexo de ordem de serviço",
                "verbose_name_plural": "anexos de ordem de serviço",
                "ordering": ["criado_em"],
            },
        ),
    ]
