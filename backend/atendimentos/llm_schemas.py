"""JSON Schemas para Structured Outputs do motor LLM."""

ACOES_UI_ENUM = [
    "",
    "confirmar_servico",
    "escolha_campo",
    "solicitar_localizacao",
    "solicitar_foto",
    "revisao_final",
    "pesquisa_satisfacao",
    "sugerir_troca_categoria",
    "acao_pular_campo",
]

CLASSIFICACAO_INTENCAO_SCHEMA = {
    "type": "object",
    "properties": {
        "servico_id": {
            "type": "string",
            "description": "UUID do serviço sugerido. Vazio se incerto.",
        },
        "confianca": {"type": "number"},
        "resposta_cidadao": {"type": "string"},
        "acao_ui": {
            "type": "string",
            "enum": ACOES_UI_ENUM,
            "description": "Use confirmar_servico ao sugerir um serviço para o cidadão confirmar.",
        },
    },
    "required": ["servico_id", "confianca", "resposta_cidadao", "acao_ui"],
    "additionalProperties": False,
}

EXTRACAO_DADOS_SCHEMA = {
    "type": "object",
    "properties": {
        "intencao_pular": {
            "type": "boolean",
            "description": "True se o cidadão declina responder o campo opcional em foco.",
        },
        "dados_extraidos": {
            "type": "object",
            "properties": {},
            "additionalProperties": {
                "anyOf": [
                    {"type": "string"},
                    {"type": "boolean"},
                    {"type": "number"},
                    {"type": "integer"},
                    {"type": "null"},
                ]
            },
            "description": "Somente campos do schema com valores extraídos da mensagem do usuário.",
        },
    },
    "required": ["dados_extraidos"],
    "additionalProperties": False,
}

# Legado — slot filling conversacional foi substituído por fluxo determinístico + EXTRACAO_DADOS_SCHEMA.
SLOT_FILLING_SCHEMA = EXTRACAO_DADOS_SCHEMA

REVISAO_SCHEMA = {
    "type": "object",
    "properties": {
        "resumo_revisao": {
            "type": "string",
            "description": "Resumo amigável dos dados coletados para o cidadão revisar.",
        },
        "resposta_cidadao": {"type": "string"},
        "acao_ui": {
            "type": "string",
            "enum": ["", "revisao_final"],
        },
    },
    "required": ["resumo_revisao", "resposta_cidadao", "acao_ui"],
    "additionalProperties": False,
}
