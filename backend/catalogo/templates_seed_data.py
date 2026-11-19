"""Definições dos modelos globais (is_template=True) para seed_templates."""

from __future__ import annotations

import uuid
from typing import Any

_NAMESPACE = uuid.UUID("a3f2c8e1-9b4d-4f6e-8c1d-2e5f7a9b0c1d")


def _tid(slug: str) -> uuid.UUID:
    return uuid.uuid5(_NAMESPACE, f"ouvia.template.{slug}")


def _schema_buraco() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    formulario = [
        {
            "name": "tipo_problema",
            "type": "select",
            "label": "Que tipo de problema na via?",
            "required": True,
            "options": [
                {"value": "buraco", "label": "Buraco"},
                {"value": "rachadura", "label": "Rachadura"},
                {"value": "afundamento", "label": "Afundamento"},
                {"value": "outro", "label": "Outro"},
            ],
            "ia_instrucao": (
                "Identifique o tipo de defeito na via (buraco, rachadura, afundamento). "
                "Se o cidadão descrever com outras palavras, mapeie para o valor mais próximo."
            ),
            "ia_repescagem": (
                "Pode descrever se é um buraco, uma rachadura ou um afundamento no asfalto?"
            ),
        },
        {
            "name": "tamanho",
            "type": "select",
            "label": "Tamanho aproximado",
            "required": True,
            "options": [
                {"value": "pequeno", "label": "Pequeno (até 50 cm)"},
                {"value": "medio", "label": "Médio (50 cm a 1 m)"},
                {"value": "grande", "label": "Grande (mais de 1 m)"},
            ],
            "ia_instrucao": "Estime o tamanho do defeito: pequeno, medio ou grande.",
        },
        {
            "name": "causa_risco",
            "type": "select",
            "label": "Oferece risco imediato?",
            "required": True,
            "options": [
                {"value": "sim", "label": "Sim"},
                {"value": "nao", "label": "Não"},
            ],
            "ia_instrucao": (
                "Pergunte se pedestres ou veículos correm risco imediato por causa do defeito."
            ),
        },
        {
            "name": "localizacao",
            "type": "geo",
            "label": "Local do problema",
            "required": True,
            "ia_instrucao": "Solicitar GPS do cidadão no mapa.",
        },
        {
            "name": "foto",
            "type": "image",
            "label": "Foto do local",
            "required": True,
            "ia_instrucao": "Solicitar ao menos uma foto nítida do buraco.",
        },
    ]
    schema = {
        "type": "object",
        "properties": {
            "tipo_problema": {
                "type": "string",
                "title": "Que tipo de problema na via?",
                "enum": ["buraco", "rachadura", "afundamento", "outro"],
                "enumNames": ["Buraco", "Rachadura", "Afundamento", "Outro"],
                "x-ouvia-ui-pergunta": "Que tipo de problema na via?",
                "x-ouvia-ia-extract": formulario[0]["ia_instrucao"],
                "x-ouvia-ia-reprompt": formulario[0]["ia_repescagem"],
            },
            "tamanho": {
                "type": "string",
                "title": "Tamanho aproximado",
                "enum": ["pequeno", "medio", "grande"],
                "enumNames": [
                    "Pequeno (até 50 cm)",
                    "Médio (50 cm a 1 m)",
                    "Grande (mais de 1 m)",
                ],
                "x-ouvia-ui-pergunta": "Tamanho aproximado",
                "x-ouvia-ia-extract": formulario[1]["ia_instrucao"],
            },
            "causa_risco": {
                "type": "string",
                "title": "Oferece risco imediato?",
                "enum": ["sim", "nao"],
                "enumNames": ["Sim", "Não"],
                "x-ouvia-ui-pergunta": "Oferece risco imediato?",
                "x-ouvia-ia-extract": formulario[2]["ia_instrucao"],
            },
            "localizacao": {
                "type": "string",
                "title": "Local do problema",
                "x-ouvia-tipo-campo": "geolocation",
                "x-ouvia-ui-pergunta": "Local do problema",
                "x-ouvia-ia-extract": formulario[3]["ia_instrucao"],
            },
            "foto": {
                "type": "string",
                "title": "Foto do local",
                "x-ouvia-tipo-campo": "image",
                "x-ouvia-ui-pergunta": "Foto do local",
                "x-ouvia-ia-extract": formulario[4]["ia_instrucao"],
            },
        },
        "required": ["tipo_problema", "tamanho", "causa_risco", "localizacao", "foto"],
        "$metadata": {
            "exige_localizacao": True,
            "exige_foto": True,
            "ia_conversacional": True,
            "ordem_campos": ["tipo_problema", "tamanho", "causa_risco", "localizacao", "foto"],
        },
    }
    return formulario, schema


def _schema_lampada() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    formulario = [
        {
            "name": "tipo_falha",
            "type": "select",
            "label": "O que está acontecendo com a iluminação?",
            "required": True,
            "options": [
                {"value": "lampada_queimada", "label": "Lâmpada queimada/apagada"},
                {"value": "acesa_dia", "label": "Lâmpada acesa durante o dia"},
                {"value": "poste_danificado", "label": "Poste danificado"},
                {"value": "fiacao_exposta", "label": "Fiação exposta"},
            ],
            "ia_instrucao": (
                "Classifique o problema de iluminação: lâmpada queimada, acesa de dia, "
                "poste danificado ou fiação exposta."
            ),
            "ia_repescagem": (
                "A lâmpada está apagada, queimada, acesa de dia ou o poste está danificado?"
            ),
        },
        {
            "name": "numero_poste",
            "type": "text",
            "label": "Número do poste (se houver)",
            "required": False,
            "ia_instrucao": "Extraia o número ou identificação do poste, se o cidadão mencionar.",
        },
        {
            "name": "localizacao",
            "type": "geo",
            "label": "Local do poste",
            "required": True,
            "ia_instrucao": "Peça ao cidadão para marcar o ponto exato no mapa.",
        },
    ]
    schema = {
        "type": "object",
        "properties": {
            "tipo_falha": {
                "type": "string",
                "title": "O que está acontecendo com a iluminação?",
                "enum": [
                    "lampada_queimada",
                    "acesa_dia",
                    "poste_danificado",
                    "fiacao_exposta",
                ],
                "enumNames": [
                    "Lâmpada queimada/apagada",
                    "Lâmpada acesa durante o dia",
                    "Poste danificado",
                    "Fiação exposta",
                ],
                "x-ouvia-ui-pergunta": formulario[0]["label"],
                "x-ouvia-ia-extract": formulario[0]["ia_instrucao"],
                "x-ouvia-ia-reprompt": formulario[0]["ia_repescagem"],
            },
            "numero_poste": {
                "type": "string",
                "title": "Número do poste (se houver)",
                "x-ouvia-ui-pergunta": formulario[1]["label"],
                "x-ouvia-ia-extract": formulario[1]["ia_instrucao"],
            },
            "localizacao": {
                "type": "string",
                "title": "Local do poste",
                "x-ouvia-tipo-campo": "geolocation",
                "x-ouvia-ui-pergunta": formulario[2]["label"],
                "x-ouvia-ia-extract": formulario[2]["ia_instrucao"],
            },
        },
        "required": ["tipo_falha", "localizacao"],
        "$metadata": {
            "exige_localizacao": True,
            "exige_foto": False,
            "ia_conversacional": True,
            "ordem_campos": ["tipo_falha", "numero_poste", "localizacao"],
        },
    }
    return formulario, schema


def _schema_dengue() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    formulario = [
        {
            "name": "tipo_foco",
            "type": "select",
            "label": "Qual é o tipo de foco?",
            "required": True,
            "options": [
                {"value": "agua_parada", "label": "Água parada (recipiente)"},
                {"value": "terreno_baldio", "label": "Terreno baldio / mato"},
                {"value": "lixo_acumulado", "label": "Lixo ou entulho acumulado"},
                {"value": "caixa_dagua_aberta", "label": "Caixa d'água destampada"},
            ],
            "ia_instrucao": (
                "Identifique o tipo de possível criadouro do mosquito: água parada, terreno, lixo ou caixa d'água."
            ),
        },
        {
            "name": "descricao",
            "type": "textarea",
            "label": "Descreva o local e a situação",
            "required": True,
            "ia_instrucao": (
                "Colete descrição objetiva do foco, período em que o cidadão observou e "
                "se há crianças ou idosos no imóvel."
            ),
            "ia_repescagem": (
                "Por favor, descreva onde está o foco e se há água parada visível ou materiais acumulados."
            ),
        },
        {
            "name": "localizacao",
            "type": "geo",
            "label": "Localização do foco",
            "required": True,
            "ia_instrucao": "Solicitar marcação no mapa do endereço do foco.",
        },
        {
            "name": "foto",
            "type": "image",
            "label": "Foto do foco (se possível)",
            "required": False,
            "ia_instrucao": "Convide o cidadão a enviar foto do criadouro, sem obrigar.",
        },
    ]
    schema = {
        "type": "object",
        "properties": {
            "tipo_foco": {
                "type": "string",
                "title": formulario[0]["label"],
                "enum": ["agua_parada", "terreno_baldio", "lixo_acumulado", "caixa_dagua_aberta"],
                "enumNames": [o["label"] for o in formulario[0]["options"]],
                "x-ouvia-ui-pergunta": formulario[0]["label"],
                "x-ouvia-ia-extract": formulario[0]["ia_instrucao"],
            },
            "descricao": {
                "type": "string",
                "title": formulario[1]["label"],
                "x-ouvia-ui-pergunta": formulario[1]["label"],
                "x-ouvia-ia-extract": formulario[1]["ia_instrucao"],
                "x-ouvia-ia-reprompt": formulario[1]["ia_repescagem"],
            },
            "localizacao": {
                "type": "string",
                "title": formulario[2]["label"],
                "x-ouvia-tipo-campo": "geolocation",
                "x-ouvia-ui-pergunta": formulario[2]["label"],
                "x-ouvia-ia-extract": formulario[2]["ia_instrucao"],
            },
            "foto": {
                "type": "string",
                "title": formulario[3]["label"],
                "x-ouvia-tipo-campo": "image",
                "x-ouvia-ui-pergunta": formulario[3]["label"],
                "x-ouvia-ia-extract": formulario[3]["ia_instrucao"],
            },
        },
        "required": ["tipo_foco", "descricao", "localizacao"],
        "$metadata": {
            "exige_localizacao": True,
            "exige_foto": False,
            "ia_conversacional": True,
            "ordem_campos": ["tipo_foco", "descricao", "localizacao", "foto"],
        },
    }
    return formulario, schema


def definicoes_templates() -> list[dict[str, Any]]:
    fb1, sc1 = _schema_buraco()
    fb2, sc2 = _schema_lampada()
    fb3, sc3 = _schema_dengue()
    return [
        {
            "id": _tid("zeladoria-tapa-buraco"),
            "nome": "Zeladoria: Tapa Buraco",
            "descricao": (
                "Modelo para registro de buracos e defeitos no asfalto, com GPS e foto, "
                "priorizando segurança de pedestres e veículos."
            ),
            "icone": "wrench-screwdriver",
            "categoria_slug": "zeladoria_urbana",
            "sla_horas": 48,
            "formulario_schema": fb1,
            "schema_formulario": sc1,
        },
        {
            "id": _tid("iluminacao-lampada"),
            "nome": "Iluminação: Lâmpada Queimada",
            "descricao": (
                "Modelo para lâmpadas apagadas ou falhas em postes, com localização obrigatória."
            ),
            "icone": "light-bulb",
            "categoria_slug": "zeladoria_urbana",
            "sla_horas": 24,
            "formulario_schema": fb2,
            "schema_formulario": sc2,
        },
        {
            "id": _tid("saude-foco-dengue"),
            "nome": "Saúde: Foco de Dengue",
            "descricao": (
                "Modelo vigilança em saúde para cidadão reportar possíveis criadouros do Aedes."
            ),
            "icone": "beaker",
            "categoria_slug": "saude",
            "sla_horas": 72,
            "formulario_schema": fb3,
            "schema_formulario": sc3,
        },
    ]