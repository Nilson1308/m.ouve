from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("atendimentos", "0004_avaliacaoprotocolo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mensagemchat",
            name="tipo_acao",
            field=models.CharField(
                blank=True,
                help_text="Comando de UI para o frontend (ex.: solicitar_gps, quick_reply:...).",
                max_length=255,
                null=True,
            ),
        ),
    ]
