from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core_auth", "0007_perfil_matriz_glpi_ui"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="avatar",
            field=models.ImageField(blank=True, null=True, upload_to="avatars/"),
        ),
    ]