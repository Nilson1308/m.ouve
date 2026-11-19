# RBAC dinâmico (padrão GLPI)

import uuid

from django.db import migrations, models
import django.db.models.deletion


def _perm(**overrides):
    base = {
        "mesa_trabalho": {
            "ler": False,
            "editar": False,
            "excluir": False,
            "despachar": False,
        },
        "painel_setorial": {
            "ler": False,
            "editar": False,
            "assinar": False,
        },
        "mapa_ia": {"acessar": False, "agrupar": False},
        "configuracoes": {"ler": False, "editar": False},
        "regras": {
            "exige_unidade": False,
            "acesso_staff": False,
            "super_admin": False,
        },
    }
    for modulo, acoes in overrides.items():
        if modulo not in base:
            base[modulo] = acoes
            continue
        base[modulo].update(acoes)
    return base


def seed_perfis_e_migrar_usuarios(apps, schema_editor):
    PerfilAcesso = apps.get_model("core_auth", "PerfilAcesso")
    Usuario = apps.get_model("core_auth", "Usuario")

    seeds = [
        (
            "super_admin",
            "Super Admin",
            "Acesso total ao sistema e configurações.",
            _perm(
                mesa_trabalho={"ler": True, "editar": True, "excluir": True, "despachar": True},
                painel_setorial={"ler": True, "editar": True, "assinar": True},
                mapa_ia={"acessar": True, "agrupar": True},
                configuracoes={"ler": True, "editar": True},
                regras={"exige_unidade": False, "acesso_staff": True, "super_admin": True},
            ),
        ),
        (
            "ouvidor",
            "Ouvidor",
            "Mesa de trabalho geral e triagem central.",
            _perm(
                mesa_trabalho={"ler": True, "editar": True, "excluir": False, "despachar": True},
                painel_setorial={"ler": True, "editar": False, "assinar": False},
                mapa_ia={"acessar": True, "agrupar": True},
                configuracoes={"ler": False, "editar": False},
                regras={"exige_unidade": False, "acesso_staff": True, "super_admin": False},
            ),
        ),
        (
            "gestor_setorial",
            "Gestor Setorial",
            "Painel da unidade e formalização de OS.",
            _perm(
                painel_setorial={"ler": True, "editar": True, "assinar": True},
                mesa_trabalho={"ler": True, "editar": False, "excluir": False, "despachar": False},
                mapa_ia={"acessar": False, "agrupar": False},
                configuracoes={"ler": False, "editar": False},
                regras={"exige_unidade": True, "acesso_staff": True, "super_admin": False},
            ),
        ),
        (
            "operador_campo",
            "Operador de Campo",
            "Execução de OS via magic link / app.",
            _perm(
                painel_setorial={"ler": True, "editar": False, "assinar": False},
                regras={"exige_unidade": True, "acesso_staff": False, "super_admin": False},
            ),
        ),
    ]

    legado_para_codigo = {
        "SUPER_ADMIN": "super_admin",
        "OUVIDOR": "ouvidor",
        "GESTOR_SETORIAL": "gestor_setorial",
        "OPERADOR_CAMPO": "operador_campo",
    }

    by_codigo = {}
    for codigo, nome, descricao, permissoes in seeds:
        obj, _ = PerfilAcesso.objects.get_or_create(
            codigo=codigo,
            defaults={
                "id": uuid.uuid4(),
                "nome": nome,
                "descricao": descricao,
                "permissoes": permissoes,
                "sistema": True,
            },
        )
        by_codigo[codigo] = obj

    for user in Usuario.objects.all():
        legado = (getattr(user, "perfil", None) or "").strip()
        codigo = legado_para_codigo.get(legado)
        if not codigo and user.is_superuser:
            codigo = "super_admin"
        elif not codigo and user.is_staff and user.unidade_id:
            codigo = "gestor_setorial"
        elif not codigo and user.is_staff:
            codigo = "ouvidor"
        if codigo and codigo in by_codigo:
            user.perfil_acesso_id = by_codigo[codigo].id
            user.save(update_fields=["perfil_acesso_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("core_auth", "0005_usuario_perfil_rbac"),
    ]

    operations = [
        migrations.CreateModel(
            name="PerfilAcesso",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "codigo",
                    models.SlugField(
                        blank=True,
                        help_text="Identificador estável para integrações (ex.: super_admin).",
                        max_length=50,
                        unique=True,
                    ),
                ),
                ("nome", models.CharField(max_length=120)),
                ("descricao", models.TextField(blank=True)),
                (
                    "permissoes",
                    models.JSONField(
                        default=dict,
                        help_text="Mapa módulo → ações booleanas (ver PERMISSOES_TEMPLATE).",
                    ),
                ),
                (
                    "sistema",
                    models.BooleanField(
                        default=False,
                        help_text="Perfis criados na migração/bootstrap; não devem ser excluídos.",
                    ),
                ),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "perfil de acesso",
                "verbose_name_plural": "perfis de acesso",
                "ordering": ["nome"],
            },
        ),
        migrations.AddField(
            model_name="usuario",
            name="perfil_acesso",
            field=models.ForeignKey(
                blank=True,
                help_text="Perfil RBAC dinâmico. Vazio para cidadãos.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="usuarios",
                to="core_auth.perfilacesso",
            ),
        ),
        migrations.RunPython(seed_perfis_e_migrar_usuarios, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="usuario",
            name="perfil",
        ),
    ]