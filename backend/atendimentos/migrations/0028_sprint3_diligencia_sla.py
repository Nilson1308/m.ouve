"""Sprint 3 — diligência com solicitante e pausa de SLA."""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("catalogo", "0014_governanca_fluxos_sprint25"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("atendimentos", "0027_sprint2_sla_cobranca"),
    ]

    operations = [
        migrations.AddField(
            model_name="configuracaoslacobranca",
            name="acao_expiracao_diligencia",
            field=models.CharField(
                choices=[
                    ("devolver_fila", "Devolver para a fila"),
                    ("encerrar_sem_resposta", "Encerrar por falta de resposta"),
                ],
                default="devolver_fila",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="configuracaoslacobranca",
            name="diligencia_ativa",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="configuracaoslacobranca",
            name="max_diligencias_por_protocolo",
            field=models.PositiveIntegerField(default=2),
        ),
        migrations.AddField(
            model_name="configuracaoslacobranca",
            name="prazo_diligencia_dias",
            field=models.PositiveIntegerField(default=5),
        ),
        migrations.AddField(
            model_name="protocolo",
            name="prazo_sla",
            field=models.DateTimeField(
                blank=True,
                help_text="Prazo absoluto do SLA (prorrogável após pausas de diligência).",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="protocolo",
            name="sla_pausado_desde",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="protocolo",
            name="status_anterior_diligencia",
            field=models.CharField(blank=True, default="", max_length=40),
        ),
        migrations.AddField(
            model_name="protocolo",
            name="tempo_sla_pausado_segundos",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="protocolo",
            name="status",
            field=models.CharField(
                choices=[
                    ("em_analise", "Em análise"),
                    ("em_andamento", "Em andamento"),
                    ("aguardando_revisao", "Aguardando revisão"),
                    ("aguardando_cidadao", "Aguardando cidadão"),
                    ("resolvido", "Resolvido"),
                    ("rejeitado", "Rejeitado"),
                ],
                default="em_analise",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="ordemservico",
            name="prazo_sla",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="ordemservico",
            name="sla_pausado_desde",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="ordemservico",
            name="status_anterior_diligencia",
            field=models.CharField(blank=True, default="", max_length=40),
        ),
        migrations.AddField(
            model_name="ordemservico",
            name="tempo_sla_pausado_segundos",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="ordemservico",
            name="status",
            field=models.CharField(
                choices=[
                    ("pendente", "Pendente"),
                    ("em_andamento", "Em andamento"),
                    ("aguardando_cidadao", "Aguardando cidadão"),
                    ("aguardando_formalizacao", "Aguardando formalização"),
                    ("aguardando_assinatura", "Aguardando assinatura"),
                    ("concluida", "Concluída"),
                    ("cancelada", "Cancelada"),
                ],
                default="pendente",
                max_length=32,
            ),
        ),
        migrations.CreateModel(
            name="DiligenciaProtocolo",
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
                ("pergunta", models.TextField()),
                ("exige_anexo", models.BooleanField(default=False)),
                ("prazo_resposta", models.DateTimeField(db_index=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("aguardando_cidadao", "Aguardando cidadão"),
                            ("respondida", "Respondida"),
                            ("expirada", "Expirada"),
                            ("cancelada", "Cancelada"),
                        ],
                        db_index=True,
                        default="aguardando_cidadao",
                        max_length=24,
                    ),
                ),
                ("resposta_cidadao", models.TextField(blank=True, default="")),
                ("anexos_ids", models.JSONField(blank=True, default=list)),
                ("respondida_em", models.DateTimeField(blank=True, null=True)),
                ("encerrada_em", models.DateTimeField(blank=True, null=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                (
                    "autor_servidor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="diligencias_criadas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "ordem_servico",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="diligencias",
                        to="atendimentos.ordemservico",
                    ),
                ),
                (
                    "protocolo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="diligencias",
                        to="atendimentos.protocolo",
                    ),
                ),
                (
                    "unidade_solicitante",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="diligencias_solicitadas",
                        to="catalogo.unidadeadministrativa",
                    ),
                ),
            ],
            options={
                "ordering": ["-criado_em"],
            },
        ),
        migrations.AddIndex(
            model_name="diligenciaprotocolo",
            index=models.Index(
                fields=["protocolo", "-criado_em"],
                name="atendimento_protoco_dilig_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="diligenciaprotocolo",
            index=models.Index(
                fields=["status", "prazo_resposta"],
                name="atendimento_status__dilig_idx",
            ),
        ),
    ]