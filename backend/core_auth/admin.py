from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from core_auth.models import (
    DispositivoPush,
    EnderecoCidadao,
    Notificacao,
    Papel,
    PerfilAcesso,
    Usuario,
)


@admin.register(Usuario)
class UsuarioAdmin(DjangoUserAdmin):
    model = Usuario
    ordering = ("cpf",)
    list_display = (
        "nome",
        "cpf",
        "email",
        "perfil_acesso",
        "unidade",
        "metodo_autenticacao",
        "is_staff",
    )
    search_fields = ("nome", "cpf", "email")
    fieldsets = (
        (None, {"fields": ("cpf", "password")}),
        (
            "Dados pessoais",
            {"fields": ("nome", "email", "telefone", "metodo_autenticacao", "perfil_acesso", "unidade")},
        ),
        ("Permissões", {"fields": ("is_active", "is_staff", "is_superuser", "papeis", "groups")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("cpf", "nome", "email", "password1", "password2"),
            },
        ),
    )


@admin.register(PerfilAcesso)
class PerfilAcessoAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo", "ativo", "sistema", "atualizado_em")
    list_filter = ("ativo", "sistema")
    search_fields = ("nome", "codigo")


admin.site.register(Papel)
admin.site.register(EnderecoCidadao)
admin.site.register(Notificacao)
admin.site.register(DispositivoPush)
