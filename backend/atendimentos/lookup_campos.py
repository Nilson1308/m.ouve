"""Validação de campos lookup (UUID) no fluxo do chat."""

from __future__ import annotations

from uuid import UUID

from catalogo.datasources import LOOKUP_DATASOURCE_EQUIPAMENTOS, LOOKUP_DATASOURCE_UNIDADES
from catalogo.models import ServicoCatalogo, UnidadeAdministrativa
from catalogo.schema_props import property_tem_lookup_datasource

from atendimentos.services.equipamento_protocolo import obter_equipamento_ativo


def _parse_uuid(valor) -> UUID | None:
    if valor is None:
        return None
    try:
        return UUID(str(valor).strip())
    except (ValueError, TypeError, AttributeError):
        return None


def campo_lookup_valido(prop: dict, valor) -> bool:
    """True só com UUID referenciando registro ativo no datasource."""
    if valor in (None, "", []):
        return False
    ds = (prop.get("x-ouvia-datasource") or "").strip()
    if not ds:
        return bool(str(valor).strip())
    if not _parse_uuid(valor):
        return False
    if ds == LOOKUP_DATASOURCE_EQUIPAMENTOS:
        return obter_equipamento_ativo(valor) is not None
    if ds == LOOKUP_DATASOURCE_UNIDADES:
        uid = _parse_uuid(valor)
        if not uid:
            return False
        return UnidadeAdministrativa.objects.filter(pk=uid, ativo=True).exists()
    return bool(str(valor).strip())


def higienizar_lookup_na_sessao(sessao) -> bool:
    """Remove UUIDs/textos inválidos de ``dados_coletados`` e persiste se mudou."""
    servico = getattr(sessao, "servico_identificado", None)
    if not servico:
        return False
    dados = dict(sessao.dados_coletados or {})
    negocio = {k: v for k, v in dados.items() if not str(k).startswith("_")}
    limpos = limpar_campos_lookup_invalidos(servico, negocio)
    props = (servico.schema_formulario or {}).get("properties") or {}
    alterou = False
    for chave in list(negocio.keys()):
        prop = props.get(chave) or {}
        if not property_tem_lookup_datasource(prop):
            continue
        if chave not in limpos and chave in dados:
            dados.pop(chave, None)
            alterou = True
    if alterou:
        sessao.dados_coletados = dados
        sessao.save(update_fields=["dados_coletados", "atualizado_em"])
    return alterou


def limpar_campos_lookup_invalidos(servico: ServicoCatalogo, dados: dict | None) -> dict:
    """Remove valores de lookup que não são UUID válido (ex.: texto inventado pelo LLM)."""
    if not dados:
        return {}
    props = (servico.schema_formulario or {}).get("properties") or {}
    out = dict(dados)
    for chave, prop in props.items():
        if not isinstance(prop, dict) or not property_tem_lookup_datasource(prop):
            continue
        if chave not in out:
            continue
        if not campo_lookup_valido(prop, out.get(chave)):
            out.pop(chave, None)
    return out