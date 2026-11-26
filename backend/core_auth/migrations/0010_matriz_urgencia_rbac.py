from django.db import migrations


def seed_pode_alterar_urgencia(apps, schema_editor):
    PerfilAcesso = apps.get_model("core_auth", "PerfilAcesso")
    liberados = {"super_admin", "ouvidor"}
    for perfil in PerfilAcesso.objects.all():
        perm = dict(perfil.permissoes or {})
        regras = dict(perm.get("regras") or {})
        regras["pode_alterar_urgencia"] = (perfil.codigo in liberados) or bool(
            regras.get("super_admin")
        )
        perm["regras"] = regras
        perfil.permissoes = perm
        perfil.save(update_fields=["permissoes", "atualizado_em"])


class Migration(migrations.Migration):
    dependencies = [
        ("core_auth", "0009_alter_perfilacesso_permissoes"),
    ]

    operations = [
        migrations.RunPython(seed_pode_alterar_urgencia, migrations.RunPython.noop),
    ]