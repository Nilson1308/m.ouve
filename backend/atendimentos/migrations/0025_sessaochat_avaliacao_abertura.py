from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("atendimentos", "0024_protocolo_triagem_sugerida"),
    ]

    operations = [
        migrations.AddField(
            model_name="sessaochat",
            name="avaliacao_abertura_em",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sessaochat",
            name="comentario_abertura",
            field=models.TextField(blank=True, default="", max_length=500),
        ),
        migrations.AddField(
            model_name="sessaochat",
            name="nota_abertura",
            field=models.PositiveSmallIntegerField(
                blank=True,
                help_text="Satisfação com o processo de abertura da solicitação no chat (1–5).",
                null=True,
            ),
        ),
    ]