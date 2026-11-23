"""Rótulos e valores legíveis para campos do schema (chat / backoffice)."""

from __future__ import annotations

from typing import Any

from atendimentos.services.equipamento_protocolo import obter_equipamento_ativo
from catalogo.datasources import LOOKUP_DATASOURCE_EQUIPAMENTOS, LOOKUP_DATASOURCE_UNIDADES
from catalogo.models import ServicoCatalogo, UnidadeAdministrativa


def _schema_props(schema: dict | None) -> dict:
    s = dict(schema or {})
    s.pop("$metadata", None)
    s.pop("$schema", None)
    return s.get("properties") or {}


def ordem_campos_exibicao(servico: ServicoCatalogo | None, dados: dict) -> list[str]:
    if not servico:
        return list(dados.keys())
    completo = servico.schema_formulario or {}
    meta = completo.get("$metadata") or {}
    ordem = meta.get("ordem_campos")
    if isinstance(ordem, list) and ordem:
        base = [str(c) for c in ordem if c]
    else:
        schema = _schema_props(completo)
        base = list(schema.get("required") or []) or list(schema.keys())
    vistos: set[str] = set()
    out: list[str] = []
    for chave in base + [k for k in dados if k not in base]:
        if chave in vistos:
            continue
        vistos.add(chave)
        out.append(chave)
    return out


def rotulo_campo_schema(prop: dict, chave: str) -> str:
    return (prop.get("title") or chave.replace("_", " ").strip() or chave).strip()


def formatar_valor_campo(prop: dict, valor: Any) -> str:
    if valor is None:
        return "—"
    if isinstance(valor, bool):
        return "Sim" if valor else "Não"
    if isinstance(valor, (int, float)):
        return str(valor)
    if isinstance(valor, list):
        items = prop.get("items") or {}
        enums = items.get("enum") or prop.get("enum") or []
        names = items.get("enumNames") or prop.get("enumNames") or []
        partes: list[str] = []
        for v in valor:
            if enums and v in enums:
                idx = enums.index(v)
                partes.append(names[idx] if idx < len(names) else str(v))
            else:
                partes.append(formatar_valor_campo(items or prop, v))
        return ", ".join(partes) if partes else "—"

    ds = (prop.get("x-ouvia-datasource") or "").strip()
    if ds == LOOKUP_DATASOURCE_EQUIPAMENTOS:
        eq = obter_equipamento_ativo(valor)
        if eq:
            return eq.nome
    if ds == LOOKUP_DATASOURCE_UNIDADES:
        uid = str(valor).strip()
        unidade = UnidadeAdministrativa.objects.filter(pk=uid, ativo=True).only("nome").first()
        if unidade:
            return unidade.nome

    enums = prop.get("enum") or []
    names = prop.get("enumNames") or []
    if enums and valor in enums:
        idx = enums.index(valor)
        if idx < len(names):
            return str(names[idx])

    s = str(valor).strip()
    return s if s else "—"


def dados_coletados_para_exibicao(
    servico: ServicoCatalogo | None,
    dados: dict | None,
) -> dict[str, str]:
    if not dados:
        return {}
    negocio = {k: v for k, v in dados.items() if not str(k).startswith("_")}
    props = _schema_props(servico.schema_formulario) if servico else {}
    out: dict[str, str] = {}
    for chave in ordem_campos_exibicao(servico, negocio):
        if chave not in negocio:
            continue
        prop = props.get(chave) or {}
        valor_fmt = formatar_valor_campo(prop, negocio.get(chave))
        if valor_fmt == "—":
            continue
        out[rotulo_campo_schema(prop, chave)] = valor_fmt
    return out