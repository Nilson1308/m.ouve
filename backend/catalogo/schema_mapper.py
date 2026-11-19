"""Monta ``schema_formulario`` (JSON Schema + $metadata) a partir de ``formulario_schema``."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def _tipo_json_campo(tipo: str) -> str:
    t = (tipo or "text").strip().lower()
    if t == "number":
        return "number"
    return "string"


def formulario_schema_para_schema_formulario(
    formulario: list | None,
    *,
    schema_base: dict | None = None,
) -> dict[str, Any]:
    """
    Espelha a lógica do front ``buildSchemaFormularioRequisitos``.
    Preserva ``$metadata`` de ``schema_base`` quando útil (ex.: regras de protocolo).
    """
    base_meta = deepcopy((schema_base or {}).get("$metadata") or {})
    properties: dict[str, Any] = {}
    required: list[str] = []
    ordem_campos: list[str] = []
    regras_elegibilidade: list[dict] = list(base_meta.get("regras_elegibilidade") or [])

    exige_localizacao = False
    tem_campo_imagem = False

    for campo in formulario or []:
        if not isinstance(campo, dict):
            continue
        name = str(campo.get("name") or "").strip()
        if not name:
            continue
        tipo = str(campo.get("type") or "text").strip().lower()
        if tipo in ("location",):
            tipo = "geo"
        titulo = (
            (campo.get("label") or campo.get("title") or "").strip()
            or name.replace("_", " ").title()
        )
        prop: dict[str, Any] = {
            "type": _tipo_json_campo(tipo),
            "title": titulo,
            "description": titulo,
            "x-ouvia-ui-pergunta": titulo,
        }
        if tipo == "textarea":
            prop["format"] = "textarea"
        if tipo == "image":
            prop["format"] = "uri"
            prop["x-ouvia-tipo-campo"] = "image"
            tem_campo_imagem = True
        if tipo in ("geo", "geolocation"):
            prop["x-ouvia-tipo-campo"] = "geolocation"
            exige_localizacao = True
        if tipo == "select":
            opcoes = campo.get("options") or []
            valores: list[str] = []
            for op in opcoes:
                if isinstance(op, dict):
                    valores.append(str(op.get("value") or op.get("label") or ""))
                else:
                    valores.append(str(op))
            valores = [v for v in valores if v.strip()]
            if valores:
                prop["enum"] = valores
                prop["enumNames"] = valores

        ia_extract = (campo.get("ia_instrucao") or "").strip()
        ia_reprompt = (campo.get("ia_repescagem") or "").strip()
        if ia_extract:
            prop["x-ouvia-ia-extract"] = ia_extract
        if ia_reprompt:
            prop["x-ouvia-ia-reprompt"] = ia_reprompt

        regra = campo.get("regra_elegibilidade")
        if isinstance(regra, dict) and regra.get("ativo"):
            regras_elegibilidade.append(deepcopy(regra))

        properties[name] = prop
        ordem_campos.append(name)
        if campo.get("required"):
            required.append(name)

    meta = {
        "exige_localizacao": exige_localizacao or bool(base_meta.get("exige_localizacao")),
        "exige_foto": tem_campo_imagem or bool(base_meta.get("exige_foto")),
        "ia_conversacional": True,
        "ordem_campos": ordem_campos,
        "regras_elegibilidade": _deduplicar_regras(regras_elegibilidade),
    }
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "$metadata": meta,
    }


def _deduplicar_regras(regras: list[dict]) -> list[dict]:
    vistas: set[str] = set()
    out: list[dict] = []
    for r in regras:
        if not isinstance(r, dict):
            continue
        chave = (
            f"{r.get('escopo')}|{r.get('campo')}|{r.get('condicao')}|{r.get('mensagem')}"
        )
        if chave in vistas:
            continue
        vistas.add(chave)
        out.append(r)
    return out