"""Persona e escopo do agente proativo (anti-IDOR)."""

from __future__ import annotations

from uuid import UUID

from rest_framework.exceptions import PermissionDenied, ValidationError

from atendimentos.services.escopo_dados import escopo_dashboard
from catalogo.models import UnidadeAdministrativa
from core_auth.rbac import usuario_e_super_admin


def _parse_uuid(valor) -> UUID | None:
    if not valor:
        return None
    try:
        return UUID(str(valor).strip())
    except (TypeError, ValueError):
        return None


def usuario_e_ouvidor_municipal(user) -> bool:
    perfil = getattr(user, "perfil_acesso", None)
    if not perfil:
        return False
    codigo = (getattr(perfil, "codigo", "") or "").strip().lower()
    return "ouvidor" in codigo


def resolver_escopo_briefing_usuario(user, query_params=None) -> tuple[str, UUID | None]:
    """
    Retorna (escopo_tipo, unidade_id).
    Gestor setorial: apenas unidade própria.
    Super admin / controladoria municipal: controladoria ou perspectivas via query.
    Ouvidor municipal: ouvidoria.
    """
    query_params = query_params or {}
    escopo = escopo_dashboard(user)

    if escopo["tipo"] == "unidade":
        uid = escopo["unidade_id"]
        if not uid:
            raise PermissionDenied("Usuário sem unidade vinculada.")
        if query_params.get("unidade_id") or query_params.get("perspectiva"):
            raise PermissionDenied("Escopo restrito à sua unidade.")
        return "unidade", uid

    if usuario_e_super_admin(user):
        persp = (query_params.get("perspectiva") or "").strip().lower()
        if persp == "ouvidoria":
            return "ouvidoria", None
        uid_param = _parse_uuid(query_params.get("unidade_id"))
        if uid_param:
            if not UnidadeAdministrativa.objects.filter(pk=uid_param, ativo=True).exists():
                raise ValidationError({"unidade_id": "Unidade inválida ou inativa."})
            return "unidade", uid_param
        return "controladoria", None

    if usuario_e_ouvidor_municipal(user):
        persp = (query_params.get("perspectiva") or "").strip().lower()
        if persp in ("controladoria", "ouvidoria", ""):
            return "ouvidoria", None
        uid_param = _parse_uuid(query_params.get("unidade_id"))
        if uid_param:
            raise PermissionDenied("Ouvidor não pode forçar outra unidade.")
        return "ouvidoria", None

    return "controladoria", None


def usuario_pode_acessar_briefing(user, briefing) -> bool:
    escopo_tipo, unidade_id = resolver_escopo_briefing_usuario(user, {})
    if briefing.escopo_tipo != escopo_tipo:
        return False
    if escopo_tipo == "unidade":
        return (
            briefing.unidade_id is not None
            and unidade_id is not None
            and str(briefing.unidade_id) == str(unidade_id)
        )
    if escopo_tipo == "unidade" and briefing.unidade_id:
        return False
    return True