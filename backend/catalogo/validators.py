"""Validação de payloads dinâmicos contra JSON Schema."""

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from rest_framework import serializers


def validar_dados_dinamicos(schema: dict, dados: dict) -> dict:
    """
    Valida ``dados`` contra ``schema``. Retorna ``dados`` se OK.
    Levanta ``serializers.ValidationError`` em caso de falha.
    """
    if not schema:
        return dados or {}

    instance = dados if dados is not None else {}
    try:
        validator = Draft202012Validator(schema)
        validator.validate(instance)
    except JsonSchemaValidationError as exc:
        path = ".".join(str(p) for p in exc.absolute_path) or "dados_dinamicos"
        raise serializers.ValidationError(
            {path: exc.message, "codigo_erro": "SCHEMA_INVALIDO"}
        ) from exc
    return instance
