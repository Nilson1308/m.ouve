"""
Exemplo canônico — Proteção Animal / Agendamento de Castração.

Espelha o que o backoffice persiste via Form Builder + Regras de Protocolo.
Ver também: docs/exemplos/protecao-animal-castracao.json e API_CONTRACT.md.
"""

from __future__ import annotations

from typing import Any

NOME_SERVICO_ALVO = "Agendamento de Castração de Animais"

MENSAGEM_IDADE = (
    "Para castração, o animal precisa ter entre 12 meses e 9 anos. "
    "Para outros casos, entre em contato com a Proteção Animal do município."
)
MENSAGEM_DOENCA = (
    "Não é possível agendar castração para animal doente ou com sintomas neste canal. "
    "Procure a Proteção Animal ou um veterinário antes de novo agendamento."
)
MENSAGEM_PROTOCOLO_COMBINADO = (
    "Pelas informações que você passou, este agendamento não pode seguir aqui. "
    "A Proteção Animal pode orientar o melhor caminho para o seu animal."
)

CONDICAO_IDADE = (
    'Bloquear se a idade informada for menor que 12 meses ou maior que 9 anos '
    '(incluindo respostas como "8 meses", "10 anos", "filhote recém-nascido").'
)
CONDICAO_DOENCA = (
    'Bloquear se o cidadão indicar que o animal está doente, com sintomas, '
    'em tratamento, ou responder "Sim" à pergunta sobre doença.'
)
CONDICAO_PROTOCOLO = (
    "Bloquear se, considerando idade e estado de saúde já informados, o animal "
    "estiver fora da faixa de 12 meses a 9 anos OU estiver doente/com sintomas, "
    "inclusive quando as duas condições aparecem juntas no protocolo."
)


def formulario_schema_exemplo() -> list[dict[str, Any]]:
    return [
        {
            "name": "tipo",
            "type": "select",
            "label": "Qual é o seu animal de estimação?",
            "required": True,
            "ia_instrucao": "Identificar se é cão ou gato.",
            "options": [
                {"value": "Cão", "label": "Cão"},
                {"value": "Gato", "label": "Gato"},
            ],
        },
        {
            "name": "idade",
            "type": "text",
            "label": "Qual a idade dele?",
            "required": True,
            "ia_instrucao": "Coletar idade em anos ou meses, de forma natural.",
            "ia_repescagem": "Pode informar em anos ou meses, por exemplo: 2 anos ou 8 meses.",
            "regra_elegibilidade": {
                "ativo": True,
                "tipo": "interpretacao",
                "campo": "idade",
                "condicao": CONDICAO_IDADE,
                "mensagem": MENSAGEM_IDADE,
            },
        },
        {
            "name": "doencas",
            "type": "select",
            "label": "Ele tem alguma doença?",
            "required": True,
            "ia_instrucao": "Perguntar se há doença, sintomas ou tratamento em andamento.",
            "options": [
                {"value": "Sim", "label": "Sim"},
                {"value": "Não", "label": "Não"},
            ],
            "regra_elegibilidade": {
                "ativo": True,
                "tipo": "interpretacao",
                "campo": "doencas",
                "condicao": CONDICAO_DOENCA,
                "mensagem": MENSAGEM_DOENCA,
            },
        },
        {
            "name": "porte",
            "type": "select",
            "label": "Qual o porte?",
            "required": True,
            "ia_instrucao": "Registrar porte: pequeno, médio ou grande.",
            "options": [
                {"value": "Pequeno", "label": "Pequeno"},
                {"value": "Médio", "label": "Médio"},
                {"value": "Grande", "label": "Grande"},
            ],
        },
        {
            "name": "localizacao",
            "type": "geo",
            "label": "Informe sua localização",
            "required": True,
            "ia_instrucao": "Solicitar GPS do tutor para orientar unidade de atendimento.",
        },
    ]


def schema_formulario_exemplo() -> dict[str, Any]:
    """JSON Schema + $metadata (igual ao build do front ``catalogoMappers``)."""
    return {
        "type": "object",
        "properties": {
            "tipo": {
                "type": "string",
                "title": "Qual é o seu animal de estimação?",
                "description": "Qual é o seu animal de estimação?",
                "enum": ["Cão", "Gato"],
                "enumNames": ["Cão", "Gato"],
                "x-ouvia-ui-pergunta": "Qual é o seu animal de estimação?",
                "x-ouvia-ia-extract": "Identificar se é cão ou gato.",
            },
            "idade": {
                "type": "string",
                "title": "Qual a idade dele?",
                "description": "Qual a idade dele?",
                "x-ouvia-ui-pergunta": "Qual a idade dele?",
                "x-ouvia-ia-extract": "Coletar idade em anos ou meses, de forma natural.",
                "x-ouvia-ia-reprompt": "Pode informar em anos ou meses, por exemplo: 2 anos ou 8 meses.",
            },
            "doencas": {
                "type": "string",
                "title": "Ele tem alguma doença?",
                "description": "Ele tem alguma doença?",
                "enum": ["Sim", "Não"],
                "enumNames": ["Sim", "Não"],
                "x-ouvia-ui-pergunta": "Ele tem alguma doença?",
                "x-ouvia-ia-extract": "Perguntar se há doença, sintomas ou tratamento em andamento.",
            },
            "porte": {
                "type": "string",
                "title": "Qual o porte?",
                "description": "Qual o porte?",
                "enum": ["Pequeno", "Médio", "Grande"],
                "enumNames": ["Pequeno", "Médio", "Grande"],
                "x-ouvia-ui-pergunta": "Qual o porte?",
                "x-ouvia-ia-extract": "Registrar porte: pequeno, médio ou grande.",
            },
            "localizacao": {
                "type": "string",
                "title": "Informe sua localização",
                "description": "Informe sua localização",
                "x-ouvia-tipo-campo": "geolocation",
                "x-ouvia-ui-pergunta": "Informe sua localização",
                "x-ouvia-ia-extract": "Solicitar GPS do tutor para orientar unidade de atendimento.",
            },
        },
        "required": ["tipo", "idade", "doencas", "porte", "localizacao"],
        "$metadata": {
            "exige_localizacao": True,
            "exige_foto": False,
            "ia_conversacional": True,
            "ordem_campos": ["tipo", "idade", "doencas", "porte", "localizacao"],
            "regras_elegibilidade": regras_elegibilidade_exemplo(),
        },
    }


def regras_elegibilidade_exemplo() -> list[dict[str, Any]]:
    return [
        {
            "ativo": True,
            "tipo": "interpretacao",
            "campo": "idade",
            "condicao": CONDICAO_IDADE,
            "mensagem": MENSAGEM_IDADE,
        },
        {
            "ativo": True,
            "tipo": "interpretacao",
            "campo": "doencas",
            "condicao": CONDICAO_DOENCA,
            "mensagem": MENSAGEM_DOENCA,
        },
        {
            "ativo": True,
            "escopo": "protocolo",
            "tipo": "interpretacao",
            "condicao": CONDICAO_PROTOCOLO,
            "mensagem": MENSAGEM_PROTOCOLO_COMBINADO,
        },
    ]