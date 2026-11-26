"""Governança de dados — escopo de querysets por unidade administrativa (sem hardcode de perfil)."""

from __future__ import annotations

from typing import Any

from django.db.models import Q, QuerySet

from atendimentos.models import Protocolo
from core_auth.rbac import perfil_exige_unidade, usuario_e_super_admin


def escopo_dashboard(user) -> dict[str, Any]:
    """
    Visão município: super admin ou perfil sem restrição setorial (sem unidade e sem ``exige_unidade``).
    Visão unidade: usuário com ``unidade_id`` vinculada ou perfil que exige unidade.
    """
    if usuario_e_super_admin(user):
        return {"tipo": "municipio", "unidade_id": None}

    unidade_id = getattr(user, "unidade_id", None)
    perfil = getattr(user, "perfil_acesso", None)
    exige_unidade = perfil_exige_unidade(perfil) if perfil else False

    if unidade_id:
        return {"tipo": "unidade", "unidade_id": unidade_id}
    if exige_unidade:
        return {"tipo": "unidade", "unidade_id": None}
    return {"tipo": "municipio", "unidade_id": None}


def q_protocolo_visivel_na_unidade(unidade_id) -> Q:
    """Protocolo pertence à unidade pela responsabilidade do serviço ou por OS vinculada."""
    return Q(servico__unidade_responsavel_id=unidade_id) | Q(
        ordens_servico__unidade_id=unidade_id
    )


def aplicar_escopo_protocolos(user, qs: QuerySet) -> QuerySet:
    escopo = escopo_dashboard(user)
    if escopo["tipo"] != "unidade":
        return qs
    uid = escopo["unidade_id"]
    if not uid:
        return qs.none()
    return qs.filter(q_protocolo_visivel_na_unidade(uid)).distinct()


def protocolo_no_escopo_usuario(user, protocolo: Protocolo) -> bool:
    if usuario_e_super_admin(user):
        return True
    escopo = escopo_dashboard(user)
    if escopo["tipo"] != "unidade":
        return True
    uid = escopo["unidade_id"]
    if not uid:
        return False
    return (
        queryset_protocolos_escopo(user, Protocolo.objects.filter(pk=protocolo.pk))
        .exists()
    )


def queryset_protocolos_escopo(user, base_qs=None) -> QuerySet:
    qs = (
        Protocolo.objects.all()
        if base_qs is None
        else base_qs
    )
    if base_qs is None:
        qs = qs.select_related(
            "servico",
            "servico__unidade_responsavel",
        )
    return aplicar_escopo_protocolos(user, qs)


def q_sessao_chat_visivel_na_unidade(unidade_id) -> Q:
    return (
        Q(servico_identificado__unidade_responsavel_id=unidade_id)
        | Q(protocolo_final__servico__unidade_responsavel_id=unidade_id)
        | Q(protocolo_final__ordens_servico__unidade_id=unidade_id)
    )


def aplicar_escopo_sessoes_chat(user, qs: QuerySet) -> QuerySet:
    escopo = escopo_dashboard(user)
    if escopo["tipo"] != "unidade":
        return qs
    uid = escopo["unidade_id"]
    if not uid:
        return qs.none()
    return qs.filter(q_sessao_chat_visivel_na_unidade(uid)).distinct()