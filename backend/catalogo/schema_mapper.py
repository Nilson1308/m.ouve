"""Monta ``schema_formulario`` (JSON Schema + $metadata) a partir de ``formulario_schema``."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from catalogo.datasources import WIDGET_PADRAO


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
        if tipo == "lookup":
            ds = (campo.get("datasource") or campo.get("x-ouvia-datasource") or "").strip()
            widget = (
                campo.get("ui_widget")
                or campo.get("x-ouvia-ui-widget")
                or WIDGET_PADRAO
            )
            prop["type"] = "string"
            prop["format"] = "uuid"
            prop["x-ouvia-datasource"] = ds
            prop["x-ouvia-ui-widget"] = str(widget).strip() or WIDGET_PADRAO
            prop["x-ouvia-tipo-campo"] = "lookup"
            filtro = campo.get("datasource_filter") or campo.get("x-ouvia-datasource-filter")
            if isinstance(filtro, dict) and filtro:
                prop["x-ouvia-datasource-filter"] = filtro
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

    fotos_obrigatorias = [
        name
        for name in required
        if ((properties.get(name) or {}).get("x-ouvia-tipo-campo") or "").strip().lower()
        == "image"
    ]
    exige_foto_meta = bool(fotos_obrigatorias)
    if not tem_campo_imagem:
        exige_foto_meta = bool(base_meta.get("exige_foto"))

    meta = {
        "exige_localizacao": exige_localizacao or bool(base_meta.get("exige_localizacao")),
        "exige_foto": exige_foto_meta,
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


def schema_formulario_para_formulario_schema(schema: dict | None) -> list[dict[str, Any]]:
    """Reconstrói ``formulario_schema`` a partir do JSON Schema publicado (serviços legados)."""
    if not isinstance(schema, dict):
        return []
    props = schema.get("properties") or {}
    if not props:
        return []

    meta = schema.get("$metadata") or {}
    ordem = list(meta.get("ordem_campos") or [])
    required = set(schema.get("required") or [])
    out: list[dict[str, Any]] = []
    vistos: set[str] = set()

    def _campo_de_prop(name: str, prop: dict) -> dict[str, Any]:
        titulo = (
            (prop.get("title") or prop.get("description") or "").strip()
            or name.replace("_", " ").title()
        )
        tipo_campo = (prop.get("x-ouvia-tipo-campo") or "").strip().lower()
        fmt = (prop.get("format") or "").strip().lower()

        if tipo_campo == "lookup" or prop.get("x-ouvia-datasource"):
            tipo = "lookup"
        elif tipo_campo in ("geolocation", "geo") or fmt == "geo":
            tipo = "geo"
        elif tipo_campo == "image" or fmt == "uri":
            tipo = "image"
        elif fmt == "textarea":
            tipo = "textarea"
        elif prop.get("type") == "number":
            tipo = "number"
        elif prop.get("enum"):
            tipo = "select"
        else:
            tipo = "text"

        item: dict[str, Any] = {
            "name": name,
            "type": tipo,
            "label": titulo,
            "required": name in required,
        }
        ia_extract = (prop.get("x-ouvia-ia-extract") or "").strip()
        ia_reprompt = (prop.get("x-ouvia-ia-reprompt") or "").strip()
        if ia_extract:
            item["ia_instrucao"] = ia_extract
        if ia_reprompt:
            item["ia_repescagem"] = ia_reprompt

        if tipo == "select":
            enums = prop.get("enumNames") or prop.get("enum") or []
            vals = [str(v) for v in (prop.get("enum") or enums)]
            labels = [str(n) for n in enums]
            item["options"] = [
                {"value": v, "label": labels[i] if i < len(labels) else v}
                for i, v in enumerate(vals)
            ]
        if tipo == "lookup":
            item["datasource"] = prop.get("x-ouvia-datasource") or ""
            item["ui_widget"] = prop.get("x-ouvia-ui-widget") or ""
        return item

    for name in ordem:
        if name not in props or name in vistos:
            continue
        vistos.add(name)
        out.append(_campo_de_prop(name, props[name] or {}))

    for name, prop in props.items():
        if name in vistos:
            continue
        out.append(_campo_de_prop(name, prop or {}))

    return out


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