"""Assinatura eletrônica hierárquica (SHA-256) — fluxo de aprovação."""

from __future__ import annotations

import hashlib
from datetime import datetime

from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

PAPEIS_GESTOR_ASSINATURA = (
    "gestor",
    "gestor_setorial",
    "dirigente",
    "supervisor",
)


def _priorizar_gestor(qs):
    return qs.filter(papeis__codigo__in=PAPEIS_GESTOR_ASSINATURA).order_by("nome").first()


def resolver_assinante_destino(solicitante, ordem):
    """
    Define o gestor/signatário (fluxo automático, sem escolha manual).

    1. Gestor/outro staff da **mesma unidade** da OS (exceto o solicitante).
    2. Se a secretaria só tem um operador: gestor da **Mesa/Ouvidoria central**
       (staff ativo sem `unidade_id` vinculada).
    """
    unidade_id = getattr(ordem, "unidade_id", None) or getattr(
        solicitante, "unidade_id", None
    )

    if unidade_id:
        qs_unidade = (
            User.objects.filter(is_staff=True, is_active=True, unidade_id=unidade_id)
            .exclude(pk=solicitante.pk)
            .distinct()
        )
        gestor = _priorizar_gestor(qs_unidade)
        if gestor:
            return gestor
        outro = qs_unidade.order_by("nome").first()
        if outro:
            return outro

    qs_central = (
        User.objects.filter(is_staff=True, is_active=True, unidade_id__isnull=True)
        .exclude(pk=solicitante.pk)
        .distinct()
    )
    gestor_central = _priorizar_gestor(qs_central)
    if gestor_central:
        return gestor_central
    return qs_central.order_by("nome").first()


def gerar_hash_assinatura_hierarquica(
    usuario_id,
    despacho_tecnico: str,
    *,
    momento=None,
) -> tuple[str, datetime]:
    """
    Gera digest SHA-256 conforme contrato Sprint 2 (aprovação hierárquica):

    concatenação sem separadores: ID do usuário + conteúdo do despacho + timestamp ISO.
    """
    momento = momento or timezone.now()
    despacho_limpo = (despacho_tecnico or "").strip()
    raw = f"{usuario_id}{despacho_limpo}{momento.isoformat()}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return digest, momento