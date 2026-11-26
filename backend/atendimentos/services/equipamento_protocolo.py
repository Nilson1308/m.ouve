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


def protocolo_possui_localizacao_cidadao(protocolo) -> bool:
    """GPS ou endereço estruturado informado pelo cidadão — não sobrescrever."""
    if protocolo.localizacao:
        return True
    dados = protocolo.dados_dinamicos or {}
    loc = dados.get("_localizacao")
    if isinstance(loc, dict):
        lat = loc.get("latitude", loc.get("lat"))
        lng = loc.get("longitude", loc.get("lng"))
        if lat is not None and lng is not None:
            return True
    return False


def herdar_localizacao_do_equipamento(protocolo, equipamento: EquipamentoPublico) -> bool:
    """
    Copia ``equipamento.localizacao`` para o protocolo quando o cidadão
    não informou coordenadas (ex.: ouvidoria textual sobre uma UBS).
    """
    if not equipamento or not equipamento.localizacao:
        return False
    if protocolo_possui_localizacao_cidadao(protocolo):
        return False
    if protocolo.localizacao:
        return False
    protocolo.localizacao = equipamento.localizacao
    from atendimentos.services.protocolo_geolocalizacao import marcar_origem_equipamento_publico

    marcar_origem_equipamento_publico(protocolo)
    return True


def sincronizar_equipamento_no_protocolo(protocolo, *, persistir: bool = True) -> EquipamentoPublico | None:
    """Grava ``protocolo.equipamento`` quando o schema traz lookup de equipamento válido."""
    if protocolo.equipamento_id:
        eq = getattr(protocolo, "equipamento", None)
        if eq and eq.ativo and eq.unidade_responsavel.ativo:
            update_fields = []
            if herdar_localizacao_do_equipamento(protocolo, eq):
                update_fields.extend(["localizacao", "origem_localizacao"])
            bairro_eq = (eq.bairro or "").strip()
            if bairro_eq:
                dados = dict(protocolo.dados_dinamicos or {})
                if dados.get("bairro") != bairro_eq:
                    dados["bairro"] = bairro_eq
                    protocolo.dados_dinamicos = dados
                    update_fields.append("dados_dinamicos")
            if persistir and update_fields:
                protocolo.save(update_fields=update_fields + ["data_atualizacao"])
            return eq

    if not protocolo.servico_id:
        return None
    eq = resolver_equipamento_de_dados(protocolo.servico, protocolo.dados_dinamicos)
    if not eq:
        return None

    protocolo.equipamento = eq
    update_fields = ["equipamento", "data_atualizacao"]
    if herdar_localizacao_do_equipamento(protocolo, eq):
        update_fields.extend(["localizacao", "origem_localizacao"])

    bairro_eq = (eq.bairro or "").strip()
    if bairro_eq:
        dados = dict(protocolo.dados_dinamicos or {})
        dados["bairro"] = bairro_eq
        protocolo.dados_dinamicos = dados
        update_fields.append("dados_dinamicos")

    if persistir:
        protocolo.save(update_fields=update_fields)
    return eq