"""Geração e validação do link mágico de evidências (painel setorial)."""

from __future__ import annotations

import hashlib
import uuid
from datetime import timedelta

from decouple import config
from django.utils import timezone

from atendimentos.models import OrdemServico

MAGIC_LINK_VALIDADE_HORAS = 48


def build_magic_link_url(token) -> str:
    base = config("PUBLIC_BASE_URL", default="").strip().rstrip("/")
    token_str = str(token)
    if base:
        return f"{base}/campo/{token_str}"
    return f"/campo/{token_str}"


def gerar_magic_link_ordem(ordem: OrdemServico) -> uuid.UUID:
    """Regenera token com validade padrão de 48h."""
    agora = timezone.now()
    token = uuid.uuid4()
    ordem.magic_link_token = token
    ordem.magic_link_gerado_em = agora
    ordem.magic_link_expira_em = agora + timedelta(hours=MAGIC_LINK_VALIDADE_HORAS)
    ordem.magic_link_acessos = 0
    updates = [
        "magic_link_token",
        "magic_link_gerado_em",
        "magic_link_expira_em",
        "magic_link_acessos",
        "atualizado_em",
    ]
    if ordem.status == OrdemServico.Status.PENDENTE:
        ordem.status = OrdemServico.Status.EM_ANDAMENTO
        updates.append("status")
    ordem.save(update_fields=updates)
    return token


def magic_link_payload(ordem: OrdemServico) -> dict | None:
    if not ordem.magic_link_token:
        return None
    return {
        "token": str(ordem.magic_link_token),
        "url": build_magic_link_url(ordem.magic_link_token),
        "gerado_em": (
            ordem.magic_link_gerado_em.strftime("%Y-%m-%dT%H:%M:%SZ")
            if ordem.magic_link_gerado_em
            else None
        ),
        "expira_em": (
            ordem.magic_link_expira_em.strftime("%Y-%m-%dT%H:%M:%SZ")
            if ordem.magic_link_expira_em
            else None
        ),
        "acessos": ordem.magic_link_acessos,
    }


def token_magic_link_valido(ordem: OrdemServico) -> bool:
    if not ordem.magic_link_token or not ordem.magic_link_expira_em:
        return False
    return timezone.now() <= ordem.magic_link_expira_em


def registrar_assinatura_hash(ordem: OrdemServico, usuario, despacho: str):
    """
    Assinatura eletrônica simples (SHA-256).
    Conteúdo assinado: ID do usuário + ID da OS + despacho técnico + timestamp ISO.
    """
    momento = timezone.now()
    despacho_limpo = (despacho or "").strip()
    raw = f"{usuario.pk}{ordem.pk}{despacho_limpo}{momento.isoformat()}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return digest, momento
