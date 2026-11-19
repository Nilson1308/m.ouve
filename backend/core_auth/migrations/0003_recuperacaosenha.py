# Generated manually for RecuperacaoSenha

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core_auth", "0002_enable_vector"),
    ]

    operations = [
        migrations.CreateModel(
            name="RecuperacaoSenha",
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
                ("token", models.CharField(db_index=True, max_length=128, unique=True)),
                (
                    "canal",
                    models.CharField(
                        choices=[
                            ("email", "E-mail"),
                            ("sms", "SMS"),
                            ("whatsapp", "WhatsApp"),
                        ],
                        max_length=12,
                    ),
                ),
                ("expira_em", models.DateTimeField()),
                ("utilizado_em", models.DateTimeField(blank=True, null=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recuperacoes_senha",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "recuperação de senha",
                "verbose_name_plural": "recuperações de senha",
                "ordering": ["-criado_em"],
            },
        ),
    ]
