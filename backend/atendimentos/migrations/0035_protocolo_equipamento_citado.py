from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("atendimentos", "0034_copiloto_gestor"),
    ]

    operations = [
        migrations.AddField(
            model_name="protocolo",
            name="equipamento_citado_nao_catalogado",
            field=models.CharField(
                blank=True,
                db_index=True,
                default="",
                help_text="Nome de equipamento citado pelo cidadão, ainda não cadastrado na base.",
                max_length=180,
            ),
        ),
    ]