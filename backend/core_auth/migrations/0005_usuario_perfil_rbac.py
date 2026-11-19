# Generated manually for Sprint 4 RBAC

from django.db import migrations, models


def atribuir_perfis_iniciais(apps, schema_editor):
    Usuario = apps.get_model("core_auth", "Usuario")
    for user in Usuario.objects.all():
        perfil = ""
        if user.is_superuser:
            perfil = "SUPER_ADMIN"
        elif user.is_staff and user.unidade_id:
            perfil = "GESTOR_SETORIAL"
        elif user.is_staff:
            perfil = "OUVIDOR"
        if perfil and user.perfil != perfil:
            Usuario.objects.filter(pk=user.pk).update(perfil=perfil)


class Migration(migrations.Migration):

    dependencies = [
        ("core_auth", "0004_setorial_magic_link"),
        ("catalogo", "0005_unidade_descricao_ativo"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="perfil",
            field=models.CharField(
                blank=True,
                choices=[
                    ("SUPER_ADMIN", "Super Admin"),
                    ("OUVIDOR", "Ouvidor"),
                    ("GESTOR_SETORIAL", "Gestor Setorial"),
                    ("OPERADOR_CAMPO", "Operador de Campo"),
                ],
                db_index=True,
                default="",
                help_text="Papel interno do servidor (painéis backoffice). Vazio para cidadãos.",
                max_length=32,
            ),
        ),
        migrations.RunPython(atribuir_perfis_iniciais, migrations.RunPython.noop),
    ]