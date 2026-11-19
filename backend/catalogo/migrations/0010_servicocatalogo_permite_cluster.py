from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogo", "0009_servico_catalogo_versionamento"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicocatalogo",
            name="permite_cluster",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Se ativo, permite agrupar protocolos próximos no mapa (ex.: zeladoria). "
                    "Desative para atendimentos individuais (ex.: assistência social)."
                ),
            ),
        ),
    ]