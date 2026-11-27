"""Resolução de equipamento no chat: UUID, texto não catalogado ou pulo."""

from __future__ import annotations

from typing import Any

from catalogo.datasources import LOOKUP_DATASOURCE_EQUIPAMENTOS
from catalogo.equipamento_utils import (
    _parse_datasource_filter,
    buscar_equipamentos_unicos_no_texto,
    campos_schema_datasource,
)
from catalogo.models import ServicoCatalogo
from catalogo.schema_props import property_tem_lookup_datasource

from atendimentos.lookup_campos import campo_lookup_valido, texto_lookup_nao_catalogado
from atendimentos.services.equipamento_protocolo import obter_equipamento_ativo


def _propriedade(servico: ServicoCatalogo, campo: str) -> dict:
    schema = servico.schema_formulario or {}
    schema.pop("$metadata", None)
    return (schema.get("properties") or {}).get(campo) or {}


def valor_nao_catalogado_dict(texto: str) -> dict[str, Any]:
    t = (texto or "").strip()[:180]
    return {"nao_catalogado": True, "texto": t}


def registrar_citacao_sessao(sessao, texto: str) -> None:
    t = (texto or "").strip()[:180]
    if not t:
        return
    dados = dict(sessao.dados_coletados or {})
    dados["_equipamento_citado_nao_catalogado"] = t
    sessao.dados_coletados = dados


def tentar_resolver_equipamento(
    sessao,
    servico: ServicoCatalogo,
    campo: str,
    valor: Any,
    *,
    texto_livre: str = "",
) -> Any | None:
    """
    Converte texto livre em UUID único, dict nao_catalogado ou None.
    Persiste citação em sessão quando não houver cadastro.
    """
    prop = _propriedade(servico, campo)
    ds = (prop.get("x-ouvia-datasource") or "").strip()
    if ds != LOOKUP_DATASOURCE_EQUIPAMENTOS:
        return valor
    if campo_lookup_valido(prop, valor):
        return valor
    texto = (texto_livre or "").strip()
    if not texto and isinstance(valor, str):
        texto = valor.strip()
    if not texto:
        return None
    if obter_equipamento_ativo(texto):
        return str(texto)
    filtro = _parse_datasource_filter(prop)
    matches = buscar_equipamentos_unicos_no_texto(
        texto,
        unidade_id=filtro.get("unidade_id"),
        tipo=filtro.get("tipo"),
    )
    if len(matches) == 1:
        return str(matches[0].id)
    if len(texto) >= 3:
        registrar_citacao_sessao(sessao, texto)
        return valor_nao_catalogado_dict(texto)
    return None


def aplicar_equipamento_em_texto_usuario(sessao, servico: ServicoCatalogo, texto: str) -> dict[str, Any]:
    """Durante passo de equipamento: se o texto cita local fora da base, aceita e avança."""
    schema = servico.schema_formulario or {}
    aplicados: dict[str, Any] = {}
    dados = {
        k: v for k, v in (sessao.dados_coletados or {}).items() if not str(k).startswith("_")
    }
    for chave in campos_schema_datasource(schema, LOOKUP_DATASOURCE_EQUIPAMENTOS):
        if dados.get(chave) not in (None, "", []):
            if campo_lookup_valido(_propriedade(servico, chave), dados.get(chave)):
                continue
        if chave in aplicados:
            continue
        resolvido = tentar_resolver_equipamento(sessao, servico, chave, None, texto_livre=texto)
        if resolvido is not None:
            aplicados[chave] = resolvido
    return aplicados