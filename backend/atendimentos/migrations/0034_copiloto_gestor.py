# Generated manually — Sprint 4.7B Copiloto Gestor

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("atendimentos", "0033_protocolo_origem_localizacao"),
        ("catalogo", "0017_sprint46_matriz_urgencia"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SessaoCopilotoGestor",
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
                ("titulo", models.CharField(max_length=140)),
                (
                    "perspectiva",
                    models.CharField(
                        choices=[
                            ("controladoria", "Controladoria"),
                            ("ouvidoria", "Ouvidoria"),
                            ("unidade", "Unidade"),
                        ],
                        max_length=24,
                    ),
                ),
                (
                    "contexto_rota_inicial",
                    models.CharField(blank=True, default="", max_length=120),
                ),
                ("criado_em", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "unidade",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sessoes_copiloto_gestor",
                        to="catalogo.unidadeadministrativa",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sessoes_copiloto",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Sessão Copiloto Gestor",
                "verbose_name_plural": "Sessões Copiloto Gestor",
                "ordering": ["-atualizado_em"],
            },
        ),
        migrations.CreateModel(
            name="MensagemCopilotoGestor",
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
                (
                    "papel",
                    models.CharField(
                        choices=[
                            ("usuario", "Usuário"),
                            ("assistente", "Assistente"),
                        ],
                        max_length=16,
                    ),
                ),
                ("conteudo", models.TextField()),
                (
                    "status_processamento",
                    models.CharField(
                        choices=[
                            ("concluida", "Concluída"),
                            ("processando", "Processando"),
                            ("erro", "Erro"),
                        ],
                        default="concluida",
                        max_length=16,
                    ),
                ),
                ("ferramentas_usadas", models.JSONField(blank=True, default=list)),
                ("referencias", models.JSONField(blank=True, default=list)),
                (
                    "modo_geracao",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("llm", "LLM"),
                            ("deterministico_fallback", "Determinístico (fallback)"),
                            ("", ""),
                        ],
                        default="",
                        max_length=32,
                    ),
                ),
                ("modelo_llm", models.CharField(blank=True, default="", max_length=80)),
                ("tokens_entrada", models.PositiveIntegerField(default=0)),
                ("tokens_saida", models.PositiveIntegerField(default=0)),
                ("erro_detalhe", models.CharField(blank=True, default="", max_length=200)),
                ("criado_em", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "sessao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mensagens",
                        to="atendimentos.sessaocopilotogestor",
                    ),
                ),
            ],
            options={
                "verbose_name": "Mensagem Copiloto Gestor",
                "verbose_name_plural": "Mensagens Copiloto Gestor",
                "ordering": ["criado_em"],
            },
        ),
    ]