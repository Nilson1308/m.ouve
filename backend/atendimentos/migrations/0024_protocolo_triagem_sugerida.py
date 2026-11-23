from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("atendimentos", "0023_onda4_notificacoes_cidadao_push"),
    ]

    operations = [
        migrations.AddField(
            model_name="protocolo",
            name="triagem_sugerida",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text=(
                    "Sugestões estruturadas do motor de triagem (determinístico/LLM) "
                    "para apoio ao despacho na Mesa."
                ),
            ),
        ),
    ]