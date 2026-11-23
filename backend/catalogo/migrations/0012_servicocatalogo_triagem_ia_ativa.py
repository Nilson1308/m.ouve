from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogo", "0011_fluxo_tramitacao_lookup_roteamento"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicocatalogo",
            name="triagem_ia_ativa",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Quando ativo, enfileira triagem semântica (LLM) para sugerir unidades "
                    "executoras em fluxos ouvidoria_encaminha e híbrido, após a triagem "
                    "determinística."
                ),
            ),
        ),
    ]