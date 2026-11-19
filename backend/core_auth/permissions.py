"""Permissões DRF do hub (RBAC dinâmico)."""

from rest_framework.permissions import BasePermission

from core_auth.rbac import (
    HasModulePermission,
    perfil_exige_unidade,
    require_permission,
    usuario_e_super_admin,
    usuario_tem_permissao,
)

__all__ = [
    "IsSuperAdmin",
    "HasModulePermission",
    "HasPermissaoGranular",
    "PermissaoPorModuloHTTP",
    "PermissaoMesaTrabalho",
    "PermissaoPainelSetorial",
    "PermissaoMapaIA",
    "PermissaoConfiguracoes",
    "PermissaoGestaoUsuarios",
    "PermissaoTextosPadrao",
    "IsBackofficeStaff",
    "IsSetorialStaff",
    "require_permission",
]

# Alias explícito para a factory (documentação / imports).
HasPermissaoGranular = require_permission


class IsSuperAdmin(BasePermission):
    """Somente perfil com regra super_admin ou superusuário Django (bootstrap)."""

    message = "Acesso restrito a Super Administradores."

    def has_permission(self, request, view):
        return usuario_e_super_admin(request.user)


_HTTP_ACAO = {
    "GET": "ler",
    "HEAD": "ler",
    "OPTIONS": "ler",
    "POST": "criar",
    "PUT": "editar",
    "PATCH": "editar",
    "DELETE": "excluir",
}


class PermissaoPorModuloHTTP(BasePermission):
    """Mapeia método HTTP → ação CRUD do módulo (`ler`/`criar`/`editar`/`excluir`)."""

    modulo: str = ""
    message = "Sem permissão para acessar este recurso."

    def _acao_requerida(self, request) -> str:
        return _HTTP_ACAO.get((request.method or "").upper(), "ler")

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        acao = self._acao_requerida(request)
        if usuario_tem_permissao(user, self.modulo, acao):
            return True
        self.message = f"Permissão necessária: {self.modulo}.{acao}."
        return False


class PermissaoMesaTrabalho(PermissaoPorModuloHTTP):
    modulo = "mesa_trabalho"
    message = "Sem permissão na Mesa de Trabalho."


class PermissaoPainelSetorial(PermissaoPorModuloHTTP):
    modulo = "painel_setorial"
    message = "Sem permissão no Painel Setorial."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        user = request.user
        if usuario_e_super_admin(user):
            return True
        perfil = getattr(user, "perfil_acesso", None)
        if perfil and perfil_exige_unidade(perfil) and not getattr(user, "unidade_id", None):
            self.message = "Perfil exige unidade administrativa vinculada."
            return False
        return True


class PermissaoMapaIA(PermissaoPorModuloHTTP):
    modulo = "mapa_ia"
    message = "Sem permissão na visão territorial / mapa IA."


class PermissaoConfiguracoes(PermissaoPorModuloHTTP):
    modulo = "configuracoes"
    message = "Sem permissão nas configurações do sistema."


class PermissaoGestaoUsuarios(PermissaoPorModuloHTTP):
    modulo = "gestao_usuarios"
    message = "Sem permissão na gestão de usuários."


class PermissaoTextosPadrao(PermissaoPorModuloHTTP):
    modulo = "textos_padrao"
    message = "Sem permissão nos textos padrão de despacho."


# Aliases legados (mantidos nos imports existentes do projeto)
IsBackofficeStaff = PermissaoMesaTrabalho
IsSetorialStaff = PermissaoPainelSetorial