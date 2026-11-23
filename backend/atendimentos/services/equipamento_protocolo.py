"""Vínculo Protocolo ↔ EquipamentoPublico a partir de dados_dinamicos."""

from __future__ import annotations

import uuid

from catalogo.equipamento_utils import campos_equipamentos_publicos_schema
from catalogo.models import EquipamentoPublico


def _parse_uuid(valor) -> uuid.UUID | None:
    if valor is None:
        return None
    try:
        return uuid.UUID(str(valor).strip())
    except (ValueError, TypeError, AttributeError):
        return None


def obter_equipamento_ativo(equipamento_id) -> EquipamentoPublico | None:
    uid = _parse_uuid(equipamento_id)
    if not uid:
        return None
    return (
        EquipamentoPublico.objects.filter(
            pk=uid,
            ativo=True,
            unidade_responsavel__ativo=True,
        )
        .select_related("unidade_responsavel")
        .first()
    )


def resolver_equipamento_de_dados(servico, dados: dict | None) -> EquipamentoPublico | None:
    schema = (servico.schema_formulario or {}) if servico else {}
    dados = dados or {}
    for chave in campos_equipamentos_publicos_schema(schema):
        eq = obter_equipamento_ativo(dados.get(chave))
        if eq:
            return eq
    return None


def sincronizar_equipamento_no_protocolo(protocolo, *, persistir: bool = True) -> EquipamentoPublico | None:
    """Grava ``protocolo.equipamento`` quando o schema traz lookup de equipamento válido."""
    if protocolo.equipamento_id:
        eq = getattr(protocolo, "equipamento", None)
        if eq and eq.ativo and eq.unidade_responsavel.ativo:
            return eq
    if not protocolo.servico_id:
        return None
    eq = resolver_equipamento_de_dados(protocolo.servico, protocolo.dados_dinamicos)
    if not eq:
        return None
    protocolo.equipamento = eq
    if persistir:
        protocolo.save(update_fields=["equipamento", "data_atualizacao"])
    return eq