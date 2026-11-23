"""Resolução de formulario_schema para edição (inclui importação legado)."""

from __future__ import annotations

from catalogo.schema_mapper import schema_formulario_para_formulario_schema


def _lista_tem_campos(lista) -> bool:
    return bool(lista) and isinstance(lista, list) and any(
        isinstance(c, dict) and (c.get("name") or "").strip() for c in lista
    )


def _schema_tem_campos(schema) -> bool:
    if not isinstance(schema, dict):
        return False
    props = schema.get("properties") or {}
    return bool(props)


def formulario_schema_para_edicao(
    *,
    formulario: list | None,
    schema_formulario: dict | None,
) -> tuple[list, bool]:
    """
    Retorna (lista de campos, importado_de_schema_json).
    Se ``formulario_schema`` está vazio mas há ``schema_formulario``, reconstrói a lista.
    """
    if _lista_tem_campos(formulario):
        return list(formulario), False
    if _schema_tem_campos(schema_formulario):
        return schema_formulario_para_formulario_schema(schema_formulario), True
    return [], False


def aplicar_resolucao_edicao_representation(data: dict, instance) -> dict:
    """Enriquece payload GET governança com formulário resolvido para o Form Builder."""
    if instance.tem_rascunho_pendente:
        lista, importado = formulario_schema_para_edicao(
            formulario=instance.formulario_schema_rascunho,
            schema_formulario=instance.schema_formulario_rascunho or instance.schema_formulario,
        )
        data["formulario_schema_rascunho"] = lista
        data["schema_legado_importado_rascunho"] = importado
    else:
        lista, importado = formulario_schema_para_edicao(
            formulario=instance.formulario_schema,
            schema_formulario=instance.schema_formulario,
        )
        data["formulario_schema"] = lista
        data["schema_legado_importado"] = importado
    return data