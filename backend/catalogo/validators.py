"""Validação de payloads dinâmicos contra JSON Schema."""

import uuid as uuid_lib

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from rest_framework import serializers

from catalogo.datasources import LOOKUP_DATASOURCE_EQUIPAMENTOS, LOOKUP_DATASOURCE_UNIDADES
from catalogo.models import EquipamentoPublico, UnidadeAdministrativa
from catalogo.schema_props import property_tem_lookup_datasource


def _valor_nao_catalogado(valor) -> bool:
    return isinstance(valor, dict) and bool((valor or {}).get("nao_catalogado"))


def _validar_uuids_lookup(schema: dict, dados: dict) -> None:
    props = (schema or {}).get("properties") or {}
    for chave, prop in props.items():
        if not property_tem_lookup_datasource(prop):
            continue
        if chave not in dados or dados.get(chave) in (None, ""):
            continue
        ds = (prop.get("x-ouvia-datasource") or "").strip()
        bruto = dados[chave]
        if _valor_nao_catalogado(bruto):
            texto = str((bruto or {}).get("texto") or "").strip()
            if ds == LOOKUP_DATASOURCE_EQUIPAMENTOS and len(texto) >= 2:
                continue
            raise serializers.ValidationError(
                {chave: "Informe o nome do local em texto ou selecione na lista."}
            )
        valor = str(bruto).strip()
        try:
            uid = uuid_lib.UUID(valor)
        except (ValueError, AttributeError) as exc:
            if ds == LOOKUP_DATASOURCE_EQUIPAMENTOS:
                msg = "Informe um identificador de equipamento válido (UUID)."
            else:
                msg = "Informe um identificador de unidade válido (UUID)."
            raise serializers.ValidationError({chave: msg}) from exc
        if ds == LOOKUP_DATASOURCE_UNIDADES:
            if not UnidadeAdministrativa.objects.filter(pk=uid, ativo=True).exists():
                raise serializers.ValidationError(
                    {chave: "Unidade administrativa não encontrada ou inativa."}
                )
        elif ds == LOOKUP_DATASOURCE_EQUIPAMENTOS:
            if not EquipamentoPublico.objects.filter(
                pk=uid,
                ativo=True,
                unidade_responsavel__ativo=True,
            ).exists():
                raise serializers.ValidationError(
                    {chave: "Equipamento não encontrado ou inativo."}
                )


def validar_dados_dinamicos(schema: dict, dados: dict) -> dict:
    """
    Valida ``dados`` contra ``schema``. Retorna ``dados`` se OK.
    Levanta ``serializers.ValidationError`` em caso de falha.
    """
    if not schema:
        return dados or {}

    instance = dict(dados if dados is not None else {})
    instance.pop("equipamento_texto_livre", None)
    _validar_uuids_lookup(schema, instance)
    props = (schema or {}).get("properties") or {}
    for chave in list(instance.keys()):
        prop = props.get(chave) or {}
        if property_tem_lookup_datasource(prop) and _valor_nao_catalogado(instance.get(chave)):
            instance.pop(chave, None)
    try:
        validator = Draft202012Validator(schema)
        validator.validate(instance)
    except JsonSchemaValidationError as exc:
        path = ".".join(str(p) for p in exc.absolute_path) or "dados_dinamicos"
        raise serializers.ValidationError(
            {path: exc.message, "codigo_erro": "SCHEMA_INVALIDO"}
        ) from exc
    return instance
