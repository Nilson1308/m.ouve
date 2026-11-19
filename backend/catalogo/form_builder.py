"""Form Builder — estrutura ``formulario_schema`` do catálogo de serviços."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from catalogo.datasources import LOOKUP_DATASOURCES, LOOKUP_UI_WIDGETS, WIDGET_PADRAO

TIPOS_CAMPO_SUPORTADOS = frozenset(
    {
        "text",
        "textarea",
        "number",
        "select",
        "lookup",
        "image",
        "geo",
        "location",
        "date",
        "boolean",
        "email",
        "tel",
    }
)

FORMULARIO_SCHEMA_EXEMPLO: list[dict[str, Any]] = [
    {
        "name": "foto_local",
        "type": "image",
        "label": "Foto do Local",
        "required": True,
    },
    {
        "name": "ponto_referencia",
        "type": "text",
        "label": "Ponto de Referência",
        "required": False,
    },
]


def formulario_schema_padrao() -> list[dict[str, Any]]:
    return deepcopy(FORMULARIO_SCHEMA_EXEMPLO)


def normalizar_regra_elegibilidade(regra: dict, *, campo_name: str) -> dict[str, Any]:
    """Normaliza regra anexada a um passo do roteiro conversacional."""
    tipo = (regra.get("tipo") or "texto").strip().lower()
    mensagem = (regra.get("mensagem") or "").strip()
    if not mensagem:
        raise ValueError(f"Campo '{campo_name}': informe a mensagem da regra de elegibilidade.")

    if tipo in ("interpretacao", "nl", "natural"):
        condicao = (regra.get("condicao") or "").strip()
        if len(condicao) < 8:
            raise ValueError(
                f"Campo '{campo_name}': descreva a condição de bloqueio (mín. 8 caracteres)."
            )
        return {
            "ativo": True,
            "tipo": "interpretacao",
            "mensagem": mensagem,
            "campo": campo_name,
            "condicao": condicao,
        }

    if tipo in ("idade", "idade_faixa"):
        try:
            min_m = int(regra.get("idade_min_meses") or 12)
        except (TypeError, ValueError):
            min_m = 12
        try:
            max_a = int(regra.get("idade_max_anos") or 9)
        except (TypeError, ValueError):
            max_a = 9
        return {
            "ativo": True,
            "tipo": "idade_faixa",
            "mensagem": mensagem,
            "campo": campo_name,
            "idade_min_meses": max(0, min_m),
            "idade_max_anos": max(0, max_a),
        }

    valores = regra.get("valores") or []
    if isinstance(valores, str):
        valores = [v.strip() for v in valores.replace(",", "\n").split("\n") if v.strip()]
    if not isinstance(valores, list):
        valores = []
    valores = [str(v).strip() for v in valores if str(v).strip()]
    if not valores:
        raise ValueError(
            f"Campo '{campo_name}': regra por texto exige ao menos um valor de bloqueio."
        )
    return {
        "ativo": True,
        "tipo": "texto",
        "mensagem": mensagem,
        "campo": campo_name,
        "valores": valores,
    }


def normalizar_formulario_schema(payload: list | None) -> list[dict[str, Any]]:
    """Valida e normaliza a lista de campos do Form Builder."""
    if payload is None:
        return []
    if not isinstance(payload, list):
        raise ValueError("formulario_schema deve ser uma lista de campos.")
    normalizado: list[dict[str, Any]] = []
    nomes_vistos: set[str] = set()
    for idx, campo in enumerate(payload):
        if not isinstance(campo, dict):
            raise ValueError(f"Campo #{idx + 1} deve ser um objeto.")
        name = str(campo.get("name") or "").strip()
        if not name:
            raise ValueError(f"Campo #{idx + 1}: 'name' é obrigatório.")
        if name in nomes_vistos:
            raise ValueError(f"Nome duplicado no formulário: {name}")
        nomes_vistos.add(name)
        tipo = str(campo.get("type") or "text").strip().lower()
        if tipo not in TIPOS_CAMPO_SUPORTADOS:
            raise ValueError(f"Campo '{name}': tipo '{tipo}' não suportado.")
        label = str(campo.get("label") or name.replace("_", " ").title()).strip()
        item: dict[str, Any] = {
            "name": name,
            "type": tipo,
            "label": label,
            "required": bool(campo.get("required", False)),
        }
        if campo.get("placeholder"):
            item["placeholder"] = str(campo["placeholder"]).strip()
        if campo.get("help_text"):
            item["help_text"] = str(campo["help_text"]).strip()
        for chave_ia in ("ia_instrucao", "ia_repescagem"):
            if campo.get(chave_ia):
                item[chave_ia] = str(campo[chave_ia]).strip()
        regra = campo.get("regra_elegibilidade")
        if regra is None and isinstance(campo.get("regra_bloqueio"), dict):
            leg = campo["regra_bloqueio"]
            regra = {
                "ativo": True,
                "tipo": "texto",
                "mensagem": leg.get("mensagem"),
                "valores": leg.get("valores"),
            }
        if isinstance(regra, dict) and regra.get("ativo"):
            item["regra_elegibilidade"] = normalizar_regra_elegibilidade(regra, campo_name=name)
        if tipo == "select" and isinstance(campo.get("options"), list):
            item["options"] = [
                {"value": str(o.get("value", o)), "label": str(o.get("label", o.get("value", o)))}
                for o in campo["options"]
                if isinstance(o, dict)
            ]
        if tipo == "lookup":
            ds = (campo.get("datasource") or campo.get("x-ouvia-datasource") or "").strip()
            if ds not in LOOKUP_DATASOURCES:
                raise ValueError(
                    f"Campo '{name}': datasource obrigatório e válido "
                    f"({', '.join(sorted(LOOKUP_DATASOURCES))})."
                )
            widget = (
                campo.get("ui_widget")
                or campo.get("x-ouvia-ui-widget")
                or WIDGET_PADRAO
            )
            widget = str(widget).strip()
            if widget not in LOOKUP_UI_WIDGETS:
                raise ValueError(
                    f"Campo '{name}': ui_widget inválido ({', '.join(sorted(LOOKUP_UI_WIDGETS))})."
                )
            item["datasource"] = ds
            item["ui_widget"] = widget
        normalizado.append(item)
    return normalizado