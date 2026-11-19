from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("atendimentos", "0005_alter_mensagemchat_tipo_acao"),
    ]

    operations = [
        migrations.AddField(
            model_name="mensagemchat",
            name="payload_ui",
            field=models.JSONField(
                blank=True,
                help_text="Snapshot de UI (ex.: config escolha_campo) no momento da mensagem.",
                null=True,
            ),
        ),
    ]
