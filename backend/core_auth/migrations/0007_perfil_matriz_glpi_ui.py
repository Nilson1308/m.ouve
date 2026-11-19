# Alinha permissões à matriz Vue (6×4) e campo ativo

from django.db import migrations, models


def atualizar_matriz_perfis(apps, schema_editor):
    PerfilAcesso = apps.get_model("core_auth", "PerfilAcesso")
    # Import tardio para lógica de migração
    from core_auth.rbac import aplicar_regras_automaticas, migrar_permissoes_legado

    presets = {
        "super_admin": {
            "mesa_trabalho": {"ler": True, "criar": True, "editar": True, "excluir": True},
            "painel_setorial": {"ler": True, "criar": True, "editar": True, "excluir": True},
            "mapa_ia": {"ler": True, "criar": True, "editar": True, "excluir": True},
            "configuracoes": {"ler": True, "criar": True, "editar": True, "excluir": True},
            "textos_padrao": {"ler": True, "criar": True, "editar": True, "excluir": True},
            "gestao_usuarios": {"ler": True, "criar": True, "editar": True, "excluir": True},
            "regras": {"exige_unidade": False, "acesso_staff": True, "super_admin": True},
        },
        "ouvidor": {
            "mesa_trabalho": {"ler": True, "criar": True, "editar": True, "excluir": False},
            "painel_setorial": {"ler": True, "criar": False, "editar": False, "excluir": False},
            "mapa_ia": {"ler": True, "criar": True, "editar": False, "excluir": False},
            "configuracoes": {"ler": False, "criar": False, "editar": False, "excluir": False},
            "textos_padrao": {"ler": True, "criar": False, "editar": False, "excluir": False},
            "gestao_usuarios": {"ler": False, "criar": False, "editar": False, "excluir": False},
            "regras": {"exige_unidade": False, "acesso_staff": True, "super_admin": False},
        },
        "gestor_setorial": {
            "mesa_trabalho": {"ler": True, "criar": False, "editar": False, "excluir": False},
            "painel_setorial": {"ler": True, "criar": True, "editar": True, "excluir": False},
            "mapa_ia": {"ler": False, "criar": False, "editar": False, "excluir": False},
            "configuracoes": {"ler": False, "criar": False, "editar": False, "excluir": False},
            "textos_padrao": {"ler": True, "criar": True, "editar": True, "excluir": True},
            "gestao_usuarios": {"ler": False, "criar": False, "editar": False, "excluir": False},
            "regras": {"exige_unidade": True, "acesso_staff": True, "super_admin": False},
        },
        "operador_campo": {
            "mesa_trabalho": {"ler": False, "criar": False, "editar": False, "excluir": False},
            "painel_setorial": {"ler": True, "criar": False, "editar": False, "excluir": False},
            "mapa_ia": {"ler": False, "criar": False, "editar": False, "excluir": False},
            "configuracoes": {"ler": False, "criar": False, "editar": False, "excluir": False},
            "textos_padrao": {"ler": False, "criar": False, "editar": False, "excluir": False},
            "gestao_usuarios": {"ler": False, "criar": False, "editar": False, "excluir": False},
            "regras": {"exige_unidade": True, "acesso_staff": False, "super_admin": False},
        },
    }

    for perfil in PerfilAcesso.objects.all():
        if perfil.codigo in presets:
            perms = aplicar_regras_automaticas(
                presets[perfil.codigo],
                requer_vinculo=presets[perfil.codigo]["regras"]["exige_unidade"],
                codigo=perfil.codigo,
                preservar_super_admin=True,
            )
        else:
            perms = aplicar_regras_automaticas(
                migrar_permissoes_legado(perfil.permissoes),
                requer_vinculo=migrar_permissoes_legado(perfil.permissoes)["regras"].get(
                    "exige_unidade"
                ),
                codigo=perfil.codigo or "",
                preservar_super_admin=migrar_permissoes_legado(perfil.permissoes)["regras"].get(
                    "super_admin", False
                ),
            )
        perfil.permissoes = perms
        perfil.ativo = True
        perfil.save(update_fields=["permissoes", "ativo", "atualizado_em"])


class Migration(migrations.Migration):

    dependencies = [
        ("core_auth", "0006_perfil_acesso_glpi"),
    ]

    operations = [
        migrations.AddField(
            model_name="perfilacesso",
            name="ativo",
            field=models.BooleanField(
                default=True,
                help_text="Perfis inativos não aparecem para vínculo em novos usuários.",
            ),
        ),
        migrations.RunPython(atualizar_matriz_perfis, migrations.RunPython.noop),
    ]