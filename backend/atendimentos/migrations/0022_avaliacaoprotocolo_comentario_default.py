from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("atendimentos", "0021_onda3_avaliacao_onetoone_csat"),
    ]

    operations = [
        migrations.AlterField(
            model_name="avaliacaoprotocolo",
            name="comentario",
            field=models.TextField(blank=True, default="", max_length=500),
        ),
    ]