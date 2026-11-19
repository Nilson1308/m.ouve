"""RBAC dinâmico (padrão GLPI) — módulos, ações e helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from rest_framework.permissions import BasePermission

ACOES_CRUD = ("ler", "criar", "editar", "excluir")

MODULOS_MATRIZ = (
    "mesa_trabalho",
    "painel_setorial",
    "mapa_ia",
    "configuracoes",
    "textos_padrao",
    "gestao_usuarios",
)

# Template canônico (matriz Vue 6×4 + metadados `regras`).
PERMISSOES_TEMPLATE: dict[str, dict[str, bool]] = {
    **{mod: {acao: False for acao in ACOES_CRUD} for mod in MODULOS_MATRIZ},
    "regras": {
        "exige_unidade": False,
        "acesso_staff": False,
        "super_admin": False,
    },
}

MODULOS_CONHECIDOS = MODULOS_MATRIZ
ACOES_POR_MODULO = {k: ACOES_CRUD for k in MODULOS_MATRIZ}

# Aliases legados (API v3.0) → matriz CRUD
_ALIASES_ACAO = {
    "mesa_trabalho": {"despachar": "criar"},
    "painel_setorial": {"assinar": "editar"},
    "mapa_ia": {"acessar": "ler", "agrupar": "criar"},
}


def permissoes_padrao() -> dict[str, Any]:
    return deepcopy(PERMISSOES_TEMPLATE)


def _aplicar_aliases_modulo(modulo: str, acoes: dict) -> dict[str, bool]:
    base = {acao: False for acao in ACOES_CRUD}
    if not isinstance(acoes, dict):
        return base
    aliases = _ALIASES_ACAO.get(modulo, {})
    for chave, valor in acoes.items():
        if chave in base:
            base[chave] = bool(valor)
        elif chave in aliases:
            destino = aliases[chave]
            base[destino] = base[destino] or bool(valor)
    return base


def migrar_permissoes_legado(payload: dict | None) -> dict[str, Any]:
    """Converte JSON antigo (despachar/assinar/acessar) para a matriz CRUD."""
    if not payload:
        return permissoes_padrao()
    base = permissoes_padrao()
    for modulo in MODULOS_MATRIZ:
        if modulo in payload:
            base[modulo] = _aplicar_aliases_modulo(modulo, payload.get(modulo) or {})
    if isinstance(payload.get("regras"), dict):
        for chave in base["regras"]:
            if chave in payload["regras"]:
                base["regras"][chave] = bool(payload["regras"][chave])
    return base


def normalizar_permissoes(payload: dict | None) -> dict[str, Any]:
    """Mescla payload do cliente com o template e força bool em cada ação."""
    merged = migrar_permissoes_legado(payload)
    return merged


def permissoes_para_matriz_ui(perfil_acesso) -> dict[str, dict[str, bool]]:
    """Retorna só os 6 módulos da matriz (sem `regras`) para o Vue."""
    permissoes = normalizar_permissoes(getattr(perfil_acesso, "permissoes", None))
    return {mod: dict(permissoes.get(mod, {})) for mod in MODULOS_MATRIZ}


def aplicar_regras_automaticas(
    permissoes: dict,
    *,
    requer_vinculo: bool | None = None,
    codigo: str | None = None,
    preservar_super_admin: bool = False,
) -> dict:
    """Deriva `regras` a partir da matriz e flags do formulário."""
    perms = normalizar_permissoes(permissoes)
    regras = perms.setdefault("regras", permissoes_padrao()["regras"])

    if requer_vinculo is not None:
        regras["exige_unidade"] = bool(requer_vinculo)

    if preservar_super_admin and regras.get("super_admin"):
        pass
    elif codigo == "super_admin":
        regras["super_admin"] = True
    else:
        go = perms.get("gestao_usuarios", {})
        cfg = perms.get("configuracoes", {})
        regras["super_admin"] = bool(
            go.get("editar") and go.get("excluir") and cfg.get("editar")
        )

    regras["acesso_staff"] = bool(
        regras.get("super_admin")
        or any(perms.get(m, {}).get("ler") for m in MODULOS_MATRIZ)
    )
    return perms


def _perfil_acesso_or_none(user) -> Any | None:
    if not user or not getattr(user, "is_authenticated", False):
        return None
    if getattr(user, "is_superuser", False):
        return None
    return getattr(user, "perfil_acesso", None)


def regras_do_perfil(perfil_acesso) -> dict[str, bool]:
    if not perfil_acesso:
        return {}
    permissoes = normalizar_permissoes(getattr(perfil_acesso, "permissoes", None))
    return permissoes.get("regras", {})


def perfil_exige_unidade(perfil_acesso) -> bool:
    return bool(regras_do_perfil(perfil_acesso).get("exige_unidade"))


def perfil_e_super_admin(perfil_acesso) -> bool:
    return bool(regras_do_perfil(perfil_acesso).get("super_admin"))


def usuario_e_super_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False):
        return True
    perfil = _perfil_acesso_or_none(user)
    return perfil is not None and perfil_e_super_admin(perfil)


def usuario_tem_permissao(user, modulo: str, acao: str) -> bool:
    """Verifica permissão no JSON do perfil. Aceita aliases legados na checagem."""
    if not user or not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False):
        return True
    perfil = getattr(user, "perfil_acesso", None)
    if perfil is None:
        return False
    if perfil_e_super_admin(perfil):
        return True
    permissoes = normalizar_permissoes(perfil.permissoes)
    modulo_norm = (modulo or "").strip()
    acao_norm = (acao or "").strip()

    if modulo_norm in _ALIASES_ACAO and acao_norm in _ALIASES_ACAO[modulo_norm]:
        acao_norm = _ALIASES_ACAO[modulo_norm][acao_norm]

    return bool(permissoes.get(modulo_norm, {}).get(acao_norm, False))


def sincronizar_flags_usuario(usuario) -> None:
    perfil = getattr(usuario, "perfil_acesso", None)
    if not perfil:
        return
    regras = regras_do_perfil(perfil)
    if regras.get("super_admin"):
        usuario.is_staff = True
        usuario.is_superuser = True
        return
    usuario.is_superuser = False
    usuario.is_staff = bool(regras.get("acesso_staff"))


class HasModulePermission(BasePermission):
    def __init__(self, modulo: str, acao: str):
        self.modulo = modulo
        self.acao = acao

    def has_permission(self, request, view):
        return usuario_tem_permissao(request.user, self.modulo, self.acao)


def make_has_module_permission(modulo: str, acao: str) -> type[BasePermission]:
    class _Perm(HasModulePermission):
        def __init__(self):
            super().__init__(modulo, acao)

    _Perm.__name__ = f"HasModulePermission_{modulo}_{acao}"
    return _Perm


def codigos_permissao_catalogo() -> list[str]:
    """Lista canônica `modulo.acao` (matriz CRUD — consumida pelo frontend)."""
    return [f"{mod}.{acao}" for mod in MODULOS_MATRIZ for acao in ACOES_CRUD]


def listar_permissoes_efetivas(user) -> list[str]:
    """Códigos granulares ativos do usuário (`mesa_trabalho.ler`, …)."""
    if not user or not getattr(user, "is_authenticated", False):
        return []
    if usuario_e_super_admin(user):
        return sorted(codigos_permissao_catalogo())
    perfil = getattr(user, "perfil_acesso", None)
    if perfil is None:
        return []
    permissoes = normalizar_permissoes(perfil.permissoes)
    ativos: list[str] = []
    for modulo in MODULOS_MATRIZ:
        for acao in ACOES_CRUD:
            if permissoes.get(modulo, {}).get(acao):
                ativos.append(f"{modulo}.{acao}")
    return sorted(ativos)


def usuario_e_backoffice(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if usuario_e_super_admin(user):
        return True
    if listar_permissoes_efetivas(user):
        return True
    return bool(getattr(user, "perfil_acesso_id", None) and getattr(user, "is_staff", False))


def usuario_e_cidadao(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    return not usuario_e_backoffice(user)


def require_permission(codigo: str) -> type[BasePermission]:
    """
    Factory DRF: `permission_classes = [IsAuthenticated, require_permission('mesa_trabalho.ler')]`
    """
    partes = (codigo or "").strip().split(".", 1)
    if len(partes) != 2 or not all(partes):
        raise ValueError(f"Código de permissão inválido: {codigo!r}")
    modulo, acao = partes

    class HasPermissaoGranular(BasePermission):
        message = f"Permissão necessária: {modulo}.{acao}."

        def has_permission(self, request, view):
            if not request.user or not request.user.is_authenticated:
                return False
            if usuario_tem_permissao(request.user, modulo, acao):
                return True
            return False

    HasPermissaoGranular.__name__ = f"HasPermissaoGranular_{modulo}_{acao}"
    return HasPermissaoGranular