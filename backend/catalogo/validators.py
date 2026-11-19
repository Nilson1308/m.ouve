"""Validação de payloads dinâmicos contra JSON Schema."""

import uuid as uuid_lib

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from rest_framework import serializers

from catalogo.schema_props import property_tem_lookup_datasource


def _validar_uuids_lookup(schema: dict, dados: dict) -> None:
    props = (schema or {}).get("properties") or {}
    for chave, prop in props.items():
        if not property_tem_lookup_datasource(prop):
            continue
        if chave not in dados or dados.get(chave) in (None, ""):
            continue
        valor = str(dados[chave]).strip()
        try:
            uuid_lib.UUID(valor)
        except (ValueError, AttributeError) as exc:
            raise serializers.ValidationError(
                {chave: "Informe um identificador de unidade válido (UUID)."}
            ) from exc


def validar_dados_dinamicos(schema: dict, dados: dict) -> dict:
    """
    Valida ``dados`` contra ``schema``. Retorna ``dados`` se OK.
    Levanta ``serializers.ValidationError`` em caso de falha.
    """
    if not schema:
        return dados or {}

    instance = dados if dados is not None else {}
    _validar_uuids_lookup(schema, instance)
    try:
        validator = Draft202012Validator(schema)
        validator.validate(instance)
    except JsonSchemaValidationError as exc:
        path = ".".join(str(p) for p in exc.absolute_path) or "dados_dinamicos"
        raise serializers.ValidationError(
            {path: exc.message, "codigo_erro": "SCHEMA_INVALIDO"}
        ) from exc
    return instance
