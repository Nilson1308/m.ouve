from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("atendimentos", "0019_protocolo_satisfacao"),
    ]

    operations = [
        migrations.AddField(
            model_name="sessaochat",
            name="motivo_inelegibilidade",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="Rótulo da regra que bloqueou o atendimento (métricas / escudo político).",
                max_length=255,
                null=True,
            ),
        ),
    ]