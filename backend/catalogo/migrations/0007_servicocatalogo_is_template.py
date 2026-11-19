from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogo", "0006_servico_form_builder"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicocatalogo",
            name="is_template",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Se True, é um modelo global da plataforma e não aparece para o cidadão."
                ),
            ),
        ),
        migrations.AddIndex(
            model_name="servicocatalogo",
            index=models.Index(
                fields=["is_template", "ativo"],
                name="catalogo_se_is_temp_8f4d2a_idx",
            ),
        ),
    ]