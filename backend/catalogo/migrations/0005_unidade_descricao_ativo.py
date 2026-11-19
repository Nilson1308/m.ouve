# Generated manually for Sprint 4 governança

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogo", "0004_unidadeadministrativa"),
    ]

    operations = [
        migrations.RenameField(
            model_name="unidadeadministrativa",
            old_name="ativa",
            new_name="ativo",
        ),
        migrations.RemoveIndex(
            model_name="unidadeadministrativa",
            name="catalogo_un_ativa_idx",
        ),
        migrations.AddIndex(
            model_name="unidadeadministrativa",
            index=models.Index(fields=["ativo"], name="catalogo_un_ativo_idx"),
        ),
        migrations.AddField(
            model_name="unidadeadministrativa",
            name="descricao",
            field=models.TextField(blank=True),
        ),
    ]