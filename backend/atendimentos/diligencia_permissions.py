"""RBAC e validações de escopo para diligência (mesa + painel setorial)."""

from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import BasePermission

from atendimentos.models import DiligenciaProtocolo, OrdemServico, Protocolo
from core_auth.rbac import usuario_e_super_admin, usuario_tem_permissao


class PermissaoDiligenciaProtocolo(BasePermission):
    """
    POST diligência: ``mesa_trabalho.criar`` (ouvidoria) **ou**
    ``painel_setorial.criar`` (gestor setorial com unidade vinculada).
    """

    message = "Sem permissão para gerenciar diligências."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if usuario_e_super_admin(user):
            return True
        if usuario_tem_permissao(user, "mesa_trabalho", "criar"):
            return True
        if usuario_tem_permissao(user, "painel_setorial", "criar"):
            if not getattr(user, "unidade_id", None):
                self.message = "Perfil setorial exige unidade administrativa vinculada."
                return False
            return True
        self.message = (
            "Permissão necessária: mesa_trabalho.criar ou painel_setorial.criar."
        )
        return False


def usuario_pode_gerir_diligencia(user, *, diligencia: DiligenciaProtocolo | None = None) -> bool:
    if usuario_e_super_admin(user):
        return True
    if usuario_tem_permissao(user, "mesa_trabalho", "criar"):
        return True
    if not usuario_tem_permissao(user, "painel_setorial", "criar"):
        return False
    uid = getattr(user, "unidade_id", None)
    if not uid:
        return False
    if diligencia and diligencia.unidade_solicitante_id != uid:
        return False
    return True


def resolver_ordem_abertura_diligencia(
    user,
    protocolo: Protocolo,
    ordem_servico_id,
) -> OrdemServico | None:
    """Valida vínculo da OS ao abrir diligência (setorial exige OS da própria unidade)."""
    if usuario_e_super_admin(user) or usuario_tem_permissao(user, "mesa_trabalho", "criar"):
        if not ordem_servico_id:
            return None
        return get_object_or_404(
            OrdemServico.objects.select_related("unidade"),
            pk=ordem_servico_id,
            protocolo_id=protocolo.pk,
        )

    if not ordem_servico_id:
        raise ValidationError(
            {"ordem_servico_id": "Informe a ordem de serviço da sua unidade."}
        )
    ordem = get_object_or_404(
        OrdemServico.objects.select_related("unidade"),
        pk=ordem_servico_id,
        protocolo_id=protocolo.pk,
    )
    if not getattr(user, "unidade_id", None) or ordem.unidade_id != user.unidade_id:
        raise PermissionDenied("A ordem de serviço não pertence à sua unidade.")
    return ordem