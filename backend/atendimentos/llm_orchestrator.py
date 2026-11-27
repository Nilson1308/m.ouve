"""
Orquestrador LLM: confirmação de serviço → slot filling → revisão → protocolo.
"""

from __future__ import annotations

import copy
import json
import logging
import time
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from django.conf import settings
from openai import APIStatusError, NotFoundError, RateLimitError
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from openai import OpenAI

from atendimentos.chat_estado import (
    FaseChat,
    confirmacao_protocolo_usuario,
    confirmacao_servico_usuario,
    get_fase,
    get_meta,
    registrar_campo_pulado,
    servico_pendente_id,
    set_meta,
    usuario_declina_informacao_campo,
)
from atendimentos.chat_intencao import detectar_intencao_pular_ou_nao_sei
from atendimentos.llm_schemas import (
    ACOES_UI_ENUM,
    CLASSIFICACAO_INTENCAO_SCHEMA,
    EXTRACAO_DADOS_SCHEMA,
)
from atendimentos.models import AnexoChatSessao, SessaoChat
from atendimentos.lookup_campos import campo_lookup_valido, higienizar_lookup_na_sessao
from catalogo.datasources import LOOKUP_DATASOURCE_EQUIPAMENTOS
from catalogo.schema_props import property_tem_lookup_datasource
from catalogo.models import ServicoCatalogo, UnidadeAdministrativa
from catalogo.catalogo_queries import filtrar_servicos_por_categoria

logger = logging.getLogger(__name__)


class ChatOrchestrationError(Exception):
    """Falha na orquestração LLM (configuração ou API)."""


SYSTEM_PROMPT_BASE = """Você é o assistente virtual do M.Ouve, ouvidoria digital municipal.
Seja empático, claro e objetivo. Use português do Brasil.

Fluxo obrigatório (não pule etapas):
A) Classificação: escolha um serviço APENAS da lista. Se confiante, pergunte se o cidadão confirma (acao_ui=confirmar_servico). NÃO colete campos do formulário ainda.
B) Preenchimento: feito pelo backend (não gere perguntas de formulário nesta etapa).
C) Revisão: feita pelo backend com acao_ui=revisao_final. NÃO diga que o protocolo já foi criado.
D) Protocolo: somente o sistema backend cria o protocolo após o cidadão confirmar na tela.

Regras anti-alucinação:
- NUNCA invente serviços fora da lista de IDs fornecida.
- NUNCA peça CPF, senha ou pagamento.
- acao_ui deve ser exatamente um valor do enum permitido ou vazio."""

ACOES_UI_VALIDAS = set(ACOES_UI_ENUM)

MSG_REVISAO = "Aqui está o resumo. Confira os dados e confirme para gerar o protocolo."
MSG_CAMPO_PULADO = "Sem problemas, vamos seguir adiante."


def _prefixar_resposta_campo_pulado(turno: TurnResult) -> TurnResult:
    if turno.resposta_cidadao:
        turno.resposta_cidadao = f"{MSG_CAMPO_PULADO}\n\n{turno.resposta_cidadao}".strip()
    else:
        turno.resposta_cidadao = MSG_CAMPO_PULADO
    return turno

_INSTRUCOES_POR_TOM_IA: dict[str, str] = {
    UnidadeAdministrativa.TomIA.INSTITUCIONAL: (
        "Tom institucional: cordial, claro e padronizado. Use linguagem respeitosa e neutra, "
        "adequada a qualquer secretaria."
    ),
    UnidadeAdministrativa.TomIA.ACOLHEDOR: (
        "Tom acolhedor: empático, gentil e paciente. Valide o sentimento do cidadão quando couber; "
        "evite pressa ou frieza."
    ),
    UnidadeAdministrativa.TomIA.OBJETIVO: (
        "Tom objetivo: direto ao ponto, ágil e conciso. Frases curtas; evite rodeios e adjetivos "
        "desnecessários."
    ),
    UnidadeAdministrativa.TomIA.TECNICO: (
        "Tom técnico: preciso e detalhista na coleta de evidências. Peça dados objetivos (quando, "
        "onde, o quê); mantenha clareza sem ser rude."
    ),
}


def _unidade_do_servico(servico: ServicoCatalogo) -> UnidadeAdministrativa | None:
    if not servico.unidade_responsavel_id:
        return None
    unidade = servico.unidade_responsavel
    if unidade is not None:
        return unidade
    return UnidadeAdministrativa.objects.filter(pk=servico.unidade_responsavel_id).first()


def _bloco_tom_secretaria(servico: ServicoCatalogo | None) -> str:
    """
    Instruções de persona da secretaria (unidade_responsável do serviço).
    Sem unidade vinculada: tom institucional padrão.
    """
    tom = UnidadeAdministrativa.TomIA.INSTITUCIONAL
    diretrizes = ""
    nome_unidade = ""
    if servico is not None:
        unidade = _unidade_do_servico(servico)
        if unidade is not None:
            tom = unidade.tom_ia or tom
            diretrizes = (unidade.diretrizes_tom_ia or "").strip()
            nome_unidade = (unidade.nome or unidade.sigla or "").strip()

    instrucao = _INSTRUCOES_POR_TOM_IA.get(
        tom, _INSTRUCOES_POR_TOM_IA[UnidadeAdministrativa.TomIA.INSTITUCIONAL]
    )
    linhas = ["## Tom de comunicação da secretaria", instrucao]
    if nome_unidade:
        linhas.append(f"Secretaria: {nome_unidade}.")
    if diretrizes:
        linhas.append(f"Diretrizes específicas da secretaria: {diretrizes}")
    return "\n".join(linhas)


def _prepend_tom_llm(mensagens: list[dict], servico: ServicoCatalogo | None) -> list[dict]:
    """Anexa bloco de tom após o primeiro system prompt, se houver."""
    bloco = _bloco_tom_secretaria(servico)
    if not bloco:
        return mensagens
    tom_msg = {"role": "system", "content": bloco}
    if mensagens and mensagens[0].get("role") == "system":
        return [mensagens[0], tom_msg, *mensagens[1:]]
    return [tom_msg, *mensagens]


@dataclass
class TurnResult:
    resposta_cidadao: str
    acao_ui: str | None
    servico_pendente_id: UUID | None = None
    confirmar_servico: bool = False
    servico_id: UUID | None = None
    dados_extraidos: dict | None = None
    ir_para_revisao: bool = False
    criar_protocolo: bool = False
    cancelar_servico_pendente: bool = False
    disparar_preenchimento_deterministico: bool = False
    config_escolha: dict | None = None
    limpar_config_escolha: bool = False
    fluxo_bloqueado: bool = False
    motivo_inelegibilidade: str | None = None
    payload_ui: dict | None = None


def _tipo_ui_campo(prop: dict) -> str:
    return (prop.get("x-ouvia-tipo-campo") or "").strip().lower()


def _msg_localizacao_servico(servico: ServicoCatalogo) -> str:
    nome = (servico.nome or "este serviço").strip()
    return f"Para dar continuidade a «{nome}», marque o local no mapa abaixo."


def _msg_foto_servico(servico: ServicoCatalogo) -> str:
    nome = (servico.nome or "esta solicitação").strip()
    return f"Se possível, envie uma foto relacionada a «{nome}» pelo botão de anexo (📷)."


def _schema_tem_campo_tipo(servico: ServicoCatalogo, tipo_ui: str) -> bool:
    schema = _schema_sem_metadados(servico.schema_formulario)
    for prop in (schema.get("properties") or {}).values():
        if _tipo_ui_campo(prop) == tipo_ui:
            return True
    return False


def _sincronizar_campos_geo_imagem(
    sessao: SessaoChat,
    servico: ServicoCatalogo,
    dados: dict,
    *,
    qtd_anexos: int = 0,
) -> dict:
    """Preenche slots geo/imagem a partir de mapa e anexos da sessão (evita pedir de novo)."""
    out = dict(dados)
    loc = (sessao.dados_coletados or {}).get("_localizacao") or {}
    endereco = (loc.get("endereco") or "").strip()
    coords_ok = loc.get("latitude") is not None and loc.get("longitude") is not None

    schema = _schema_sem_metadados(servico.schema_formulario)
    for campo in _ordem_campos_schema(servico):
        prop = (schema.get("properties") or {}).get(campo) or {}
        tipo = _tipo_ui_campo(prop)
        if tipo == "geolocation" and coords_ok and not (out.get(campo) or "").strip():
            if endereco:
                out[campo] = endereco
            else:
                out[campo] = f"{loc.get('latitude')},{loc.get('longitude')}"
        if tipo == "image" and qtd_anexos >= 1 and campo not in out:
            out[campo] = "anexo_sessao"
    return out


def _sanitizar_extraidos_campos_especiais(
    servico: ServicoCatalogo,
    extraidos: dict | None,
    sessao: SessaoChat | None,
    *,
    texto_usuario: str = "",
) -> dict:
    """Texto livre não satisfaz campo de mapa/foto — evita pular para revisão sem GPS."""
    if not extraidos:
        return {}
    limpos = dict(_filtrar_extraidos(extraidos))
    schema = _schema_sem_metadados(servico.schema_formulario)
    from atendimentos.lookup_campos import valor_lookup_nao_catalogado
    from atendimentos.services.chat_equipamento_lookup import tentar_resolver_equipamento

    for chave in list(limpos.keys()):
        prop = (schema.get("properties") or {}).get(chave) or {}
        tipo = _tipo_ui_campo(prop)
        if tipo == "geolocation":
            if not sessao or not _localizacao_ok(sessao):
                limpos.pop(chave, None)
        if tipo == "image" and sessao and _qtd_anexos(sessao) < 1:
            limpos.pop(chave, None)
        if property_tem_lookup_datasource(prop):
            val = limpos.get(chave)
            if valor_lookup_nao_catalogado(val):
                continue
            if not campo_lookup_valido(prop, val) and sessao:
                resolvido = tentar_resolver_equipamento(
                    sessao,
                    servico,
                    chave,
                    val,
                    texto_livre=texto_usuario or (str(val) if isinstance(val, str) else ""),
                )
                if resolvido is not None:
                    limpos[chave] = resolvido
                    from atendimentos.chat_sandbox import is_sessao_sandbox

                    if not is_sessao_sandbox(sessao):
                        sessao.save(update_fields=["dados_coletados", "atualizado_em"])
                else:
                    limpos.pop(chave, None)
            elif not campo_lookup_valido(prop, val):
                limpos.pop(chave, None)
    return limpos


def _regras_elegibilidade_servico(servico: ServicoCatalogo) -> list[dict]:
    meta = (servico.schema_formulario or {}).get("$metadata") or {}
    regras = meta.get("regras_elegibilidade")
    if isinstance(regras, list) and regras:
        return regras
    out: list[dict] = []
    for campo in servico.formulario_schema or []:
        if not isinstance(campo, dict):
            continue
        regra = campo.get("regra_elegibilidade")
        if isinstance(regra, dict) and regra.get("ativo"):
            copia = dict(regra)
            copia.setdefault("campo", campo.get("name"))
            out.append(copia)
    return out


def _avaliar_regras_elegibilidade(servico: ServicoCatalogo, dados: dict) -> str | None:
    mensagem, _ = _avaliar_regras_elegibilidade_detalhe(servico, dados)
    return mensagem


def _avaliar_regras_elegibilidade_detalhe(
    servico: ServicoCatalogo, dados: dict
) -> tuple[str | None, str | None]:
    from catalogo.eligibility import avaliar_regras_campos_com_motivo

    regras = _regras_elegibilidade_servico(servico)
    schema = _schema_sem_metadados(servico.schema_formulario)
    props = schema.get("properties") or {}
    nome = (servico.nome or "").strip()
    return avaliar_regras_campos_com_motivo(
        regras, dados, props, nome_servico=nome, servico=servico
    )


def _propriedade_campo(servico: ServicoCatalogo, campo: str) -> dict:
    schema = _schema_sem_metadados(servico.schema_formulario)
    return (schema.get("properties") or {}).get(campo) or {}


def _tipo_efetivo_campo(prop: dict) -> str:
    tipo = prop.get("type")
    if tipo == "array":
        items = prop.get("items") or {}
        return str(items.get("type") or "array")
    return str(tipo or "string")


def _enum_do_campo(prop: dict) -> list | None:
    if prop.get("type") == "array":
        items = prop.get("items") or {}
        enum_vals = items.get("enum")
    else:
        enum_vals = prop.get("enum")
    return enum_vals if enum_vals else None


def _modo_selecao_campo(prop: dict) -> str:
    explicit = (prop.get("x-ouvia-selection") or "").strip().lower()
    if explicit in ("single", "multi"):
        return explicit
    if prop.get("type") == "array":
        return "multi"
    return "single"


def _permite_outro_campo(prop: dict, enum_vals: list | None) -> bool:
    if prop.get("x-ouvia-allow-other") is False:
        return False
    if prop.get("x-ouvia-allow-other") is True:
        return True
    if enum_vals and any(str(v).lower() == "outro" for v in enum_vals):
        return True
    return False


def _montar_config_escolha(servico: ServicoCatalogo, campo: str) -> dict | None:
    prop = _propriedade_campo(servico, campo)
    datasource = (prop.get("x-ouvia-datasource") or "").strip()
    schema = _schema_sem_metadados(servico.schema_formulario)
    required_set = set(schema.get("required") or [])
    opcional = campo not in required_set
    if datasource == "unidades_administrativas":
        titulo = (
            prop.get("x-ouvia-ui-pergunta")
            or prop.get("description")
            or prop.get("title")
            or campo.replace("_", " ")
        ).strip()
        return {
            "campo": campo,
            "titulo": titulo,
            "modo": "single",
            "datasource": datasource,
            "opcional": opcional,
            "dica": "Selecione a unidade na lista. Os dados vêm do cadastro municipal.",
        }
    if datasource == LOOKUP_DATASOURCE_EQUIPAMENTOS:
        titulo = (
            prop.get("x-ouvia-ui-pergunta")
            or prop.get("description")
            or prop.get("title")
            or campo.replace("_", " ")
        ).strip()
        filtro = prop.get("x-ouvia-datasource-filter") or {}
        if not isinstance(filtro, dict):
            filtro = {}
        return {
            "campo": campo,
            "titulo": titulo,
            "modo": "single",
            "datasource": datasource,
            "opcional": opcional,
            "filtro": filtro,
            "dica": "Selecione o equipamento na lista ou busque pelo nome.",
        }
    enum_vals = _enum_do_campo(prop)
    if not enum_vals:
        return None
    labels = prop.get("enumNames")
    if prop.get("type") == "array":
        labels = (prop.get("items") or {}).get("enumNames") or labels
    labels = labels or enum_vals
    opcoes = [
        {"valor": str(v), "rotulo": str(l)}
        for v, l in zip(enum_vals, labels, strict=False)
    ]
    titulo = (
        prop.get("x-ouvia-ui-pergunta") or prop.get("description") or prop.get("title") or campo.replace("_", " ")
    ).strip()
    modo = _modo_selecao_campo(prop)
    permite_outro = _permite_outro_campo(prop, enum_vals)
    if modo == "multi":
        dica = "Selecione uma ou mais opções e confirme."
    else:
        dica = "Toque em uma opção abaixo."
    if permite_outro:
        dica += " Se não estiver na lista, use o campo livre."
    return {
        "campo": campo,
        "titulo": titulo,
        "modo": modo,
        "permite_outro": permite_outro,
        "opcoes": opcoes,
        "dica": dica,
    }


def _titulo_apenas_cru(prop: dict) -> bool:
    titulo = (prop.get("title") or "").strip()
    pergunta = (prop.get("x-ouvia-ui-pergunta") or prop.get("description") or "").strip()
    if pergunta:
        return False
    if not titulo:
        return False
    cru = {
        "observações adicionais",
        "observacoes adicionais",
        "enviar foto",
        "enviar imagem",
        "descreva sua manifestação",
        "descreva sua manifestacao",
    }
    return titulo.lower() in cru or titulo == titulo.upper()


def _pergunta_humanizada_fallback(prop: dict, campo: str, *, opcional: bool) -> str:
    tipo_ui = _tipo_ui_campo(prop)
    if tipo_ui == "image":
        if opcional:
            return (
                "Você gostaria de enviar alguma foto para ajudar a equipe a visualizar o problema? "
                "Se não tiver agora, pode tocar em Pular."
            )
        return "Se puder, envie uma foto pelo botão de anexo — isso ajuda muito a equipe em campo."
    if (prop.get("format") or "").lower() == "textarea" or "observ" in campo.lower():
        if opcional:
            return (
                "Deseja acrescentar mais algum detalhe ou observação? "
                "Se já estiver tudo completo, pode responder «não» ou tocar em Pular."
            )
        return "Pode me contar com mais detalhes o que aconteceu para registrarmos sua manifestação?"
    if tipo_ui == "geolocation":
        return "Para localizar o problema, marque o ponto no mapa abaixo."
    if property_tem_lookup_datasource(prop):
        return "Se souber, escolha o local na lista ou digite o nome; se não achar, descreva em texto."
    titulo = (prop.get("title") or campo.replace("_", " ")).strip()
    if opcional:
        return f"Se quiser, pode informar {titulo.lower()} — ou toque em Pular para seguir."
    return f"Pode me contar sobre {titulo.lower()}?"


def _texto_pergunta_campo(prop: dict, campo: str, *, opcional: bool = False) -> str:
    """Pergunta exibida ao cidadão (configurada no gestor de serviços)."""
    pergunta = (prop.get("x-ouvia-ui-pergunta") or prop.get("description") or "").strip()
    if pergunta and not _titulo_apenas_cru(prop):
        return pergunta
    if (prop.get("title") or "").strip() and not _titulo_apenas_cru(prop) and not pergunta:
        return (prop.get("title") or "").strip()
    return _pergunta_humanizada_fallback(prop, campo, opcional=opcional)


def _ia_metadados_campo(servico: ServicoCatalogo, campo: str, prop: dict) -> tuple[str, str]:
    """Instrução de extração e repescagem (schema JSON + formulario_schema legado)."""
    extract = (prop.get("x-ouvia-ia-extract") or "").strip()
    reprompt = (prop.get("x-ouvia-ia-reprompt") or "").strip()
    lista = servico.formulario_schema or []
    if isinstance(lista, list):
        for item in lista:
            if not isinstance(item, dict):
                continue
            if (item.get("name") or "").strip() == campo:
                extract = extract or (item.get("ia_instrucao") or "").strip()
                reprompt = reprompt or (item.get("ia_repescagem") or "").strip()
                break
    return extract, reprompt


PERGUNTA_CAMPO_SCHEMA = {
    "type": "object",
    "properties": {"pergunta": {"type": "string"}},
    "required": ["pergunta"],
    "additionalProperties": False,
}


def _redigir_pergunta_campo_llm(
    *,
    servico: ServicoCatalogo,
    campo: str,
    prop: dict,
    ia_instrucao: str,
    historico_resumo: list[str] | None = None,
) -> str | None:
    """Gera pergunta natural a partir da instrução no-code do gestor."""
    ia_instrucao = (ia_instrucao or "").strip()
    if not ia_instrucao:
        return None
    base = _texto_pergunta_campo(prop, campo)
    contexto = {
        "servico": (servico.nome or "").strip(),
        "campo": campo,
        "pergunta_gestor": base,
        "instrucao_gestor": ia_instrucao,
        "tipo_ui": _tipo_ui_campo(prop) or "texto",
        "historico_recente": (historico_resumo or [])[-4:],
    }
    mensagens = _prepend_tom_llm(
        [
            {
                "role": "system",
                "content": (
                    "Você redige UMA pergunta curta, em português do Brasil, "
                    "para o assistente municipal M.Ouve. "
                    "Siga a instrução do gestor. Não repita 'Ótimo', 'Agora' nem o nome técnico do campo. "
                    "Não peça localização nem foto no texto se o tipo_ui for geolocation ou image "
                    "(o app mostra mapa/foto). Retorne JSON {\"pergunta\": \"...\"}."
                ),
            },
            {"role": "user", "content": json.dumps(contexto, ensure_ascii=False)},
        ],
        servico,
    )
    try:
        parsed = _chamar_json_estruturado(
            nome_schema="pergunta_campo",
            schema=PERGUNTA_CAMPO_SCHEMA,
            mensagens=mensagens,
            strict=True,
        )
        texto = (parsed.get("pergunta") or "").strip()
        return texto or None
    except (ChatOrchestrationError, Exception):
        logger.warning("Falha ao redigir pergunta LLM para campo %s", campo)
        return None


def _valor_campo_extraido_valido(servico: ServicoCatalogo, campo: str, valor) -> bool:
    """False quando a extração não preencheu o slot de forma aceitável (vazio ou fora do enum)."""
    if valor is None:
        return False
    if isinstance(valor, str) and not valor.strip():
        return False
    if isinstance(valor, list):
        itens = [v for v in valor if v is not None and (not isinstance(v, str) or v.strip())]
        if not itens:
            return False
        valor = itens
    prop = _propriedade_campo(servico, campo)
    enum_vals = _enum_do_campo(prop)
    if not enum_vals:
        return True
    canon = {str(v) for v in enum_vals}
    if prop.get("type") == "array":
        if not isinstance(valor, list):
            return False
        for item in valor:
            s = str(item).strip()
            if s not in canon and s.lower() != "outro":
                return False
        return True
    s = str(valor).strip()
    return s in canon or s.lower() == "outro"


def _campo_e_opcional(servico: ServicoCatalogo, campo: str) -> bool:
    schema = _schema_sem_metadados(servico.schema_formulario)
    required = set(schema.get("required") or [])
    return bool(campo) and campo not in required


def _campo_aceita_resposta_binaria(
    servico: ServicoCatalogo, campo: str, prop: dict | None = None
) -> bool:
    """Sim/não curtos preenchem o slot (evita loop quando o LLM não extrai «sim»)."""
    prop = prop or _propriedade_campo(servico, campo)
    tipo_ui = (prop.get("x-ouvia-tipo-campo") or "").strip().lower()
    if tipo_ui in ("geolocation", "image", "lookup"):
        return False
    if prop.get("type") == "boolean":
        return True
    if tipo_ui in ("boolean", "yes_no", "sim_nao"):
        return True
    if (prop.get("format") or "").strip().lower() == "textarea":
        return False
    if _enum_do_campo(prop) or prop.get("type") == "array":
        return False
    if prop.get("type") == "string" and _campo_e_opcional(servico, campo):
        rotulo = (
            (prop.get("title") or "")
            + " "
            + (prop.get("x-ouvia-ui-pergunta") or "")
        ).lower()
        if any(
            m in rotulo
            for m in (
                "risco imediato",
                "oferece risco",
                "há risco",
                "ha risco",
                "sim ou não",
                "sim ou nao",
            )
        ):
            return True
    return False


def _extrair_resposta_binaria_campo(
    servico: ServicoCatalogo, campo: str, texto_usuario: str
) -> Any | None:
    if not _campo_aceita_resposta_binaria(servico, campo):
        return None
    decisao = confirmacao_servico_usuario(texto_usuario)
    if decisao is None:
        return None
    prop = _propriedade_campo(servico, campo)
    if prop.get("type") == "boolean":
        return decisao
    return "sim" if decisao else "não"


def _pular_opcional_se_declinio(
    sessao: SessaoChat,
    servico: ServicoCatalogo,
    campo: str | None,
    texto_usuario: str,
    *,
    intencao_pular_llm: bool = False,
) -> bool:
    """Se o cidadão declina informação em campo opcional, marca como pulado."""
    if not campo or not _campo_e_opcional(servico, campo):
        return False
    if not (
        usuario_declina_informacao_campo(texto_usuario)
        or detectar_intencao_pular_ou_nao_sei(
            texto_usuario,
            campo=campo,
            obrigatorio=False,
            extracao_llm={"intencao_pular": intencao_pular_llm} if intencao_pular_llm else None,
        )
    ):
        return False
    registrar_campo_pulado(sessao, campo)
    meta = dict(get_meta(sessao))
    tentativas = dict(meta.get("tentativas_campo") or {})
    tentativas.pop(campo, None)
    set_meta(sessao, tentativas_campo=tentativas)
    return True


def _remover_declinio_disfarcado_extraidos(
    sessao: SessaoChat,
    servico: ServicoCatalogo,
    extraidos: dict | None,
) -> dict:
    """LLM às vezes grava o próprio 'não tenho' como valor — trata como pulo."""
    if not extraidos:
        return {}
    out = dict(extraidos)
    for campo, valor in list(out.items()):
        if not _campo_e_opcional(servico, campo):
            continue
        if isinstance(valor, str) and usuario_declina_informacao_campo(valor):
            out.pop(campo, None)
            registrar_campo_pulado(sessao, campo)
    return out


def _deve_repescar_campo(
    servico: ServicoCatalogo,
    campo_foco: str | None,
    texto_usuario: str,
    extraidos_limpos: dict | None,
    sessao: SessaoChat | None = None,
) -> bool:
    """Repescagem quando o cidadão respondeu mas o slot esperado não foi preenchido ou é inválido."""
    if not campo_foco or not _deve_extrair_texto(texto_usuario):
        return False
    if _campo_e_opcional(servico, campo_foco) and (
        usuario_declina_informacao_campo(texto_usuario)
        or detectar_intencao_pular_ou_nao_sei(texto_usuario, campo=campo_foco, obrigatorio=False)
    ):
        return False
    if sessao and _campo_e_opcional(servico, campo_foco):
        tentativas = dict(get_meta(sessao).get("tentativas_campo") or {})
        if int(tentativas.get(campo_foco) or 0) >= 1:
            registrar_campo_pulado(sessao, campo_foco)
            return False
    limpos = extraidos_limpos or {}
    if campo_foco not in limpos:
        if sessao and _campo_e_opcional(servico, campo_foco):
            tentativas = dict(get_meta(sessao).get("tentativas_campo") or {})
            tentativas[campo_foco] = int(tentativas.get(campo_foco) or 0) + 1
            set_meta(sessao, tentativas_campo=tentativas)
        return True
    return not _valor_campo_extraido_valido(servico, campo_foco, limpos.get(campo_foco))


def _pergunta_para_campo(
    servico: ServicoCatalogo,
    campo: str,
    *,
    repescagem: bool = False,
    historico_resumo: list[str] | None = None,
) -> str:
    prop = _propriedade_campo(servico, campo)
    opcional = _campo_e_opcional(servico, campo)
    base = _texto_pergunta_campo(prop, campo, opcional=opcional)
    ia_extract, ia_reprompt = _ia_metadados_campo(servico, campo, prop)

    if repescagem:
        if ia_reprompt:
            return ia_reprompt
        return base

    if ia_extract:
        redigida = _redigir_pergunta_campo_llm(
            servico=servico,
            campo=campo,
            prop=prop,
            ia_instrucao=ia_extract,
            historico_resumo=historico_resumo,
        )
        if redigida:
            base = redigida

    if _montar_config_escolha(servico, campo):
        return base
    return base


def _resumo_historico_sandbox(sessao) -> list[str]:
    hist = getattr(sessao, "historico", None)
    if not isinstance(hist, list):
        return []
    linhas: list[str] = []
    for item in hist[-8:]:
        if not isinstance(item, dict):
            continue
        role = (item.get("role") or "user").strip()
        content = (item.get("content") or "").strip()
        if content:
            linhas.append(f"{role}: {content}")
    return linhas


def _acao_ui_para_campo(servico: ServicoCatalogo, campo: str) -> str | None:
    if _montar_config_escolha(servico, campo):
        return "escolha_campo"
    prop = _propriedade_campo(servico, campo)
    tipo_ui = (prop.get("x-ouvia-tipo-campo") or "").strip().lower()
    if tipo_ui == "geolocation":
        return "solicitar_localizacao"
    if tipo_ui == "image":
        return "solicitar_foto"
    return None


def _filtrar_extraidos(extraidos: dict | None) -> dict:
    if not extraidos:
        return {}
    limpos = {}
    for chave, valor in extraidos.items():
        if str(chave).startswith("_"):
            continue
        if valor is None:
            continue
        if isinstance(valor, str) and not valor.strip():
            continue
        if isinstance(valor, list):
            itens = [v for v in valor if v is not None and (not isinstance(v, str) or v.strip())]
            if not itens:
                continue
            limpos[chave] = itens
            continue
        limpos[chave] = valor
    return limpos


def _deve_extrair_texto(texto_usuario: str) -> bool:
    t = (texto_usuario or "").strip()
    if not t or t == "(sem texto)":
        return False
    if t.startswith("(") and "cidadão" in t.lower():
        return False
    return True


def _cliente_llm() -> OpenAI:
    api_key = (getattr(settings, "LLM_CHAT_API_KEY", "") or "").strip()
    base_url = getattr(settings, "LLM_CHAT_BASE_URL", "") or None
    if not api_key:
        raise ChatOrchestrationError(
            "Chave LLM não configurada. Defina GROQ_API_KEY (ou OPENAI_API_KEY) no .env."
        )
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url.rstrip("/")
    return OpenAI(**kwargs)


def _modelos_fallback() -> list[str]:
    principal = (getattr(settings, "LLM_CHAT_MODEL", "") or "").strip()
    candidatos = [
        principal,
        "openai/gpt-oss-20b",
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-120b",
        "allam-2-7b",
    ]
    vistos: set[str] = set()
    ordem: list[str] = []
    for mid in candidatos:
        if mid and mid not in vistos:
            vistos.add(mid)
            ordem.append(mid)
    return ordem


def _modelo() -> str:
    modelos = _modelos_fallback()
    return modelos[0] if modelos else "openai/gpt-oss-20b"


def _provider() -> str:
    return getattr(settings, "LLM_CHAT_PROVIDER", "groq")


def _limite_historico() -> int:
    return int(getattr(settings, "LLM_CHAT_HISTORICO_LIMITE", 14))


def _max_tokens_resposta() -> int:
    return int(getattr(settings, "LLM_CHAT_MAX_TOKENS", 768))


def _historico(sessao: SessaoChat, limite: int | None = None) -> list[dict[str, str]]:
    limite = limite if limite is not None else _limite_historico()
    linhas = []
    for msg in sessao.mensagens.order_by("criado_em")[:limite]:
        role = "user" if msg.autor == "cidadao" else ("assistant" if msg.autor == "ia" else "system")
        linhas.append({"role": role, "content": msg.conteudo_texto})
    return linhas


def _servicos_candidatos(sessao: SessaoChat) -> list[ServicoCatalogo]:
    qs = ServicoCatalogo.objects.filter(ativo=True, is_template=False).select_related(
        "categoria"
    )
    if sessao.categoria_inicial:
        qs = filtrar_servicos_por_categoria(qs, sessao.categoria_inicial)
    return list(qs)


def _servicos_outras_categorias(sessao: SessaoChat, *, limite: int = 48) -> list[ServicoCatalogo]:
    na_categoria = {str(s.id) for s in _servicos_candidatos(sessao)}
    qs = (
        ServicoCatalogo.objects.filter(ativo=True, is_template=False)
        .select_related("categoria")
        .order_by("nome")
    )
    return [s for s in qs if str(s.id) not in na_categoria][:limite]


def _montar_payload_troca_categoria(
    sessao: SessaoChat,
    servico: ServicoCatalogo,
    *,
    mensagem_original: str,
    motivo: str,
) -> dict:
    cat_atual = (sessao.categoria_inicial or "").strip()
    cat_sug = servico.categoria
    return {
        "tipo_acao": "sugerir_troca_categoria",
        "categoria_atual": {
            "slug": (cat_atual or "geral").lower().replace(" ", "-"),
            "nome": cat_atual or "categoria atual",
        },
        "categoria_sugerida": {
            "slug": (getattr(cat_sug, "slug", None) or "").strip(),
            "nome": (getattr(cat_sug, "nome", None) or "").strip(),
        },
        "servico_sugerido": {"id": str(servico.id), "nome": servico.nome},
        "mensagem_original": (mensagem_original or "")[:600],
        "motivo": (motivo or "").strip()[:400],
    }


def _catalogo_para_prompt(servicos: list[ServicoCatalogo]) -> str:
    itens = [
        {
            "id": str(s.id),
            "nome": s.nome,
            "descricao": (s.descricao or "")[:400],
            "categoria": s.categoria.nome if s.categoria_id else "",
        }
        for s in servicos
    ]
    return json.dumps(itens, ensure_ascii=False)


def _dados_negocio(sessao: SessaoChat) -> dict[str, Any]:
    return {k: v for k, v in (sessao.dados_coletados or {}).items() if not str(k).startswith("_")}


def _localizacao_ok(sessao: SessaoChat) -> bool:
    loc = (sessao.dados_coletados or {}).get("_localizacao") or {}
    return loc.get("latitude") is not None and loc.get("longitude") is not None


def _qtd_anexos(sessao: SessaoChat) -> int:
    qtd_sandbox = getattr(sessao, "sandbox_qtd_anexos", None)
    if qtd_sandbox is not None:
        return int(qtd_sandbox)
    return AnexoChatSessao.objects.filter(sessao=sessao).count()


def _exige_foto(servico: ServicoCatalogo) -> bool:
    meta = (servico.schema_formulario or {}).get("$metadata") or {}
    if meta.get("exige_foto") is True:
        return True
    if meta.get("exige_foto") is False:
        return False
    return _schema_tem_campo_tipo(servico, "image")


def _anexo_sessao_obrigatorio(sessao: SessaoChat, servico: ServicoCatalogo) -> bool:
    """
    Anexo na sessão é exigido só fora do fluxo por campo ``image`` no schema
    (quando o formulário já tem passo de foto, use required + _campos_faltantes).
    """
    if _qtd_anexos(sessao) >= 1:
        return False
    if _schema_tem_campo_tipo(servico, "image"):
        return False
    return _exige_foto(servico)


def _schema_sem_metadados(schema: dict) -> dict:
    s = copy.deepcopy(schema or {})
    s.pop("$metadata", None)
    s.pop("$schema", None)
    return s


def _ordem_campos_schema(servico: ServicoCatalogo) -> list[str]:
    completo = servico.schema_formulario or {}
    meta = completo.get("$metadata") or {}
    ordem = meta.get("ordem_campos")
    if isinstance(ordem, list) and ordem:
        return [str(c) for c in ordem if c]
    schema = _schema_sem_metadados(completo)
    required = list(schema.get("required") or [])
    if required:
        return required
    return list((schema.get("properties") or {}).keys())


def _campo_ainda_falta(
    servico: ServicoCatalogo,
    campo: str,
    prop: dict,
    dados: dict,
    sessao: SessaoChat | None,
) -> bool:
    tipo = _tipo_ui_campo(prop)
    if tipo == "geolocation":
        return not (sessao and _localizacao_ok(sessao))
    if tipo == "image":
        if sessao and _qtd_anexos(sessao) >= 1:
            return False
        valor = dados.get(campo)
        return valor is None or (isinstance(valor, str) and not valor.strip())

    valor = dados.get(campo)
    if prop.get("type") == "array":
        if not isinstance(valor, list) or len(valor) < 1:
            return True
        if any(str(v).lower() == "outro" for v in valor):
            outro_key = f"{campo}_outro"
            det = dados.get(outro_key)
            return det is None or (isinstance(det, str) and not det.strip())
        return False
    if property_tem_lookup_datasource(prop):
        return not campo_lookup_valido(prop, valor)
    if prop.get("type") == "boolean":
        return valor is None
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return True
    if isinstance(valor, str) and valor.lower() == "outro":
        outro_key = f"{campo}_outro"
        det = dados.get(outro_key)
        return det is None or (isinstance(det, str) and not det.strip())
    return False


def _campos_pulados(sessao: SessaoChat | None) -> set[str]:
    if not sessao:
        return set()
    raw = (sessao.dados_coletados or {}).get("_campos_pulados")
    if not isinstance(raw, list):
        return set()
    return {str(c).strip() for c in raw if str(c).strip()}


def _campos_faltantes(
    servico: ServicoCatalogo, dados: dict, sessao: SessaoChat | None = None
) -> list[str]:
    schema = _schema_sem_metadados(servico.schema_formulario)
    faltantes = []
    campos_ordem = _ordem_campos_schema(servico)
    pulados = _campos_pulados(sessao)
    for campo in campos_ordem:
        if campo in pulados:
            continue
        prop = (schema.get("properties") or {}).get(campo) or {}
        if _campo_ainda_falta(servico, campo, prop, dados, sessao):
            faltantes.append(campo)

    def _posicao_ordem(campo: str) -> int:
        try:
            return campos_ordem.index(campo)
        except ValueError:
            return 999

    faltantes.sort(key=_posicao_ordem)
    return faltantes


def _dados_completos(
    servico: ServicoCatalogo, dados: dict, sessao: SessaoChat | None = None
) -> bool:
    schema = _schema_sem_metadados(servico.schema_formulario)
    if not schema.get("properties"):
        return True
    if _campos_faltantes(servico, dados, sessao):
        return False
    try:
        Draft202012Validator(schema).validate(dados)
        return True
    except JsonSchemaValidationError:
        # Campos obrigatórios preenchidos; tipos vindos do LLM podem divergir do schema estrito.
        return True


def _schema_resumido_para_prompt(schema: dict) -> str:
    s = _schema_sem_metadados(schema)
    meta = schema.get("$metadata") or {}
    resumo = {
        "required": s.get("required") or [],
        "properties": {
            k: {"type": v.get("type"), "title": v.get("title"), "enum": v.get("enum")}
            for k, v in (s.get("properties") or {}).items()
        },
        "exige_localizacao": meta.get("exige_localizacao", False),
        "exige_foto": meta.get("exige_foto", False),
    }
    return json.dumps(resumo, ensure_ascii=False)


def _extrair_json_resposta(raw: str) -> dict:
    if not raw:
        raise ChatOrchestrationError("Resposta vazia do modelo.")
    texto = raw.strip()
    if texto.startswith("```"):
        linhas = texto.split("\n")
        if linhas[0].startswith("```"):
            linhas = linhas[1:]
        if linhas and linhas[-1].strip() == "```":
            linhas = linhas[:-1]
        texto = "\n".join(linhas).strip()
    try:
        return json.loads(texto)
    except json.JSONDecodeError as exc:
        raise ChatOrchestrationError("JSON inválido retornado pelo modelo.") from exc


def _instrucao_json_compacta(nome_schema: str) -> str:
    """Evita repetir schema inteiro no prompt (menos tokens de entrada)."""
    dicas = {
        "classificacao_intencao": (
            "Campos JSON: servico_id (string UUID ou vazio), confianca (número 0-1), "
            "resposta_cidadao (string), acao_ui (enum permitido ou vazio)."
        ),
        "extracao_dados": (
            "Campos JSON: dados_extraidos (objeto) com chaves do schema e valores extraídos "
            "da última mensagem do usuário. Use null ou omita campos não mencionados."
        ),
    }
    base = dicas.get(nome_schema, f"Schema lógico: {nome_schema}")
    return f"Responda APENAS com um único objeto JSON válido, sem markdown. {base}"


def _mensagem_limite_taxa(exc: BaseException) -> str:
    return (
        "O assistente está temporariamente no limite de uso da IA. "
        "Aguarde cerca de um minuto e envie a mensagem novamente."
    )


def _extrair_tokens_usage(
    response,
    mensagens: list[dict[str, str]],
    texto_resposta: str,
) -> tuple[int, int, bool]:
    """Retorna (entrada, saída, estimado)."""
    usage = getattr(response, "usage", None)
    if usage is not None:
        ent = int(getattr(usage, "prompt_tokens", 0) or 0)
        sai = int(getattr(usage, "completion_tokens", 0) or 0)
        if ent or sai:
            return ent, sai, False
    est_in = sum(len(m.get("content") or "") for m in mensagens) // 4
    est_out = max(1, len(texto_resposta or "") // 4)
    return max(est_in, 1), est_out, True


def _chamar_json_estruturado(
    *,
    nome_schema: str,
    schema: dict,
    mensagens: list[dict[str, str]],
    strict: bool = True,
    usage_sink: list | None = None,
) -> dict:
    client = _cliente_llm()
    modelos = _modelos_fallback()
    provider = _provider()
    max_tokens = _max_tokens_resposta()

    if provider == "groq":
        schema_instrucao = {
            "role": "system",
            "content": _instrucao_json_compacta(nome_schema),
        }
    else:
        schema_instrucao = {
            "role": "system",
            "content": (
                f"Responda APENAS com JSON válido (sem markdown), schema '{nome_schema}':\n"
                f"{json.dumps(schema, ensure_ascii=False)}"
            ),
        }
    msgs = [*mensagens, schema_instrucao]

    ultimo_erro: BaseException | None = None

    def _criar(model: str, max_out: int):
        if provider == "openai":
            return client.chat.completions.create(
                model=model,
                temperature=0.2,
                max_tokens=max_out,
                messages=mensagens,
                response_format={
                    "type": "json_schema",
                    "json_schema": {"name": nome_schema, "strict": strict, "schema": schema},
                },
            )
        return client.chat.completions.create(
            model=model,
            temperature=0.2,
            max_tokens=max_out,
            messages=msgs,
            response_format={"type": "json_object"},
        )

    response = None
    for model in modelos:
        try:
            response = _criar(model, max_tokens)
            if model != modelos[0]:
                logger.warning("LLM: modelo %s indisponível; usando %s.", modelos[0], model)
            break
        except NotFoundError as exc:
            ultimo_erro = exc
            logger.warning("Modelo Groq não disponível nesta conta: %s", model)
            continue
        except (RateLimitError, APIStatusError) as exc:
            status = getattr(exc, "status_code", None)
            if status == 429 or isinstance(exc, RateLimitError):
                logger.warning("LLM rate limit (%s) em %s: %s", provider, model, exc)
                time.sleep(2.5)
                try:
                    response = _criar(model, min(384, max_tokens))
                    break
                except (RateLimitError, APIStatusError) as retry_exc:
                    raise ChatOrchestrationError(_mensagem_limite_taxa(retry_exc)) from retry_exc
            logger.exception("Erro na API LLM (%s)", provider)
            raise ChatOrchestrationError(f"Falha ao consultar o modelo: {exc}") from exc
        except Exception as exc:
            logger.exception("Erro na API LLM (%s)", provider)
            raise ChatOrchestrationError(f"Falha ao consultar o modelo: {exc}") from exc

    if response is None:
        raise ChatOrchestrationError(
            "Modelo de IA configurado não está disponível na sua conta Groq. "
            "Defina GROQ_CHAT_MODEL para um ID listado em GET /openai/v1/models "
            f"(ex.: openai/gpt-oss-20b). Detalhe: {ultimo_erro}"
        ) from ultimo_erro

    bruto = response.choices[0].message.content or ""
    parsed = _extrair_json_resposta(bruto)
    if usage_sink is not None:
        ent, sai, estimado = _extrair_tokens_usage(response, msgs, bruto)
        usage_sink[:] = [ent, sai, estimado]
        if estimado:
            logger.info(
                "LLM usage ausente (%s); estimativa conservadora in=%s out=%s",
                provider,
                ent,
                sai,
            )
    return parsed


def _validar_servico_id(servico_id: str, permitidos: set[str]) -> str | None:
    sid = (servico_id or "").strip()
    if not sid or sid not in permitidos:
        if sid:
            logger.warning("LLM servico_id fora do catálogo: %s", sid)
        return None
    return sid


def _normalizar_acao(acao: str | None) -> str | None:
    acao = (acao or "").strip()
    if acao == "solicitar_gps":
        acao = "solicitar_localizacao"
    if acao not in ACOES_UI_VALIDAS or acao == "":
        return None
    return acao


def avaliar_pronto_revisao(sessao: SessaoChat) -> bool:
    if not sessao.servico_identificado_id:
        return False
    servico = sessao.servico_identificado
    dados = _dados_negocio(sessao)
    if _campos_faltantes(servico, dados, sessao):
        return False
    if (
        servico.exige_localizacao
        and not _localizacao_ok(sessao)
        and not _schema_tem_campo_tipo(servico, "geolocation")
    ):
        return False
    if _anexo_sessao_obrigatorio(sessao, servico):
        return False
    return True


class LLMOrchestrator:
    def processar_turno(
        self,
        sessao: SessaoChat,
        *,
        texto_usuario: str,
        anexos_novos: int = 0,
        confirmar_protocolo: bool = False,
        dados_slot: dict | None = None,
    ) -> TurnResult:
        from atendimentos.chat_estado import usuario_pediu_confirmar_protocolo

        if dados_slot:
            if dados_slot.get("forcar_categoria_atual"):
                set_meta(sessao, forcar_categoria_atual=True, troca_categoria_pendente=None)
                sessao.save(update_fields=["dados_coletados", "atualizado_em"])
            if dados_slot.get("recusar_troca_categoria"):
                pend = get_meta(sessao).get("troca_categoria_pendente") or {}
                sid = (pend.get("servico_sugerido") or {}).get("id")
                set_meta(
                    sessao,
                    troca_categoria_pendente=None,
                    forcar_categoria_atual=True,
                    troca_categoria_recusada=str(sid) if sid else None,
                )
                sessao.save(update_fields=["dados_coletados", "atualizado_em"])
            if dados_slot.get("aceitar_troca_categoria"):
                pend = get_meta(sessao).get("troca_categoria_pendente") or {}
                sid_raw = (pend.get("servico_sugerido") or {}).get("id")
                if sid_raw:
                    try:
                        sid = UUID(str(sid_raw))
                        cat_nome = (pend.get("categoria_sugerida") or {}).get("nome") or ""
                        if cat_nome:
                            sessao.categoria_inicial = cat_nome
                        set_meta(
                            sessao,
                            troca_categoria_pendente=None,
                            forcar_categoria_atual=None,
                        )
                        sessao.save(
                            update_fields=["categoria_inicial", "dados_coletados", "atualizado_em"]
                        )
                        return TurnResult(
                            resposta_cidadao="Ótimo, vamos seguir com o serviço mais adequado ao seu relato.",
                            acao_ui="confirmar_servico",
                            servico_pendente_id=sid,
                            confirmar_servico=True,
                        )
                    except (TypeError, ValueError):
                        pass

        fase = get_fase(sessao)
        pendente = servico_pendente_id(sessao)

        if usuario_pediu_confirmar_protocolo(
            texto=texto_usuario, confirmar_protocolo=confirmar_protocolo
        ):
            if sessao.servico_identificado_id and fase in (
                FaseChat.REVISAO,
                FaseChat.PREENCHIMENTO,
            ):
                if avaliar_pronto_revisao(sessao):
                    servico = sessao.servico_identificado
                    dados = _dados_negocio(sessao)
                    bloqueio, motivo = (
                        _avaliar_regras_elegibilidade_detalhe(servico, dados) if servico else (None, None)
                    )
                    if bloqueio:
                        return TurnResult(
                            resposta_cidadao=bloqueio,
                            acao_ui=None,
                            fluxo_bloqueado=True,
                            limpar_config_escolha=True,
                            motivo_inelegibilidade=motivo,
                        )
                    return TurnResult(
                        resposta_cidadao="Perfeito! Estou registrando seu protocolo agora.",
                        acao_ui=None,
                        criar_protocolo=True,
                    )
                servico = sessao.servico_identificado
                dados = _dados_negocio(sessao)
                faltantes = _campos_faltantes(servico, dados)
                partes = []
                if faltantes:
                    partes.append(f"Campos pendentes: {', '.join(faltantes)}.")
                if servico.exige_localizacao and not _localizacao_ok(sessao):
                    partes.append("Falta confirmar a localização no mapa.")
                if _anexo_sessao_obrigatorio(sessao, servico):
                    partes.append("Envie ao menos uma foto do problema.")
                msg = " ".join(partes) if partes else "Ainda faltam informações para concluir."
                set_meta(sessao, fase=FaseChat.PREENCHIMENTO)
                sessao.save(update_fields=["dados_coletados", "atualizado_em"])
                return TurnResult(
                    resposta_cidadao=msg,
                    acao_ui="solicitar_localizacao"
                    if servico.exige_localizacao and not _localizacao_ok(sessao)
                    else (
                        "solicitar_foto" if _anexo_sessao_obrigatorio(sessao, servico) else None
                    ),
                )

        if fase == FaseChat.REVISAO:
            return self._estagio_revisao(sessao, texto_usuario=texto_usuario)

        if (
            fase == FaseChat.AGUARDANDO_CONFIRMACAO_SERVICO
            or (pendente and not sessao.servico_identificado_id)
        ):
            return self._estagio_confirmacao_servico(sessao, texto_usuario=texto_usuario)

        if sessao.servico_identificado_id:
            return self._estagio_slot_filling(
                sessao,
                texto_usuario=texto_usuario,
                anexos_novos=anexos_novos,
                dados_slot=dados_slot,
            )

        return self._estagio_classificacao(sessao, texto_usuario=texto_usuario)

    def _estagio_confirmacao_servico(self, sessao: SessaoChat, *, texto_usuario: str) -> TurnResult:
        pendente = servico_pendente_id(sessao)
        if not pendente:
            return TurnResult(
                resposta_cidadao="Vamos recomeçar: o que você gostaria de reportar?",
                acao_ui=None,
                cancelar_servico_pendente=True,
            )

        decisao = confirmacao_servico_usuario(texto_usuario)
        if decisao is False:
            return TurnResult(
                resposta_cidadao="Sem problemas! Descreva novamente o que você precisa.",
                acao_ui=None,
                cancelar_servico_pendente=True,
            )
        if decisao is True:
            return TurnResult(
                resposta_cidadao="",
                acao_ui=None,
                servico_id=pendente,
                disparar_preenchimento_deterministico=True,
            )

        try:
            servico = ServicoCatalogo.objects.get(pk=pendente, ativo=True)
        except ServicoCatalogo.DoesNotExist:
            return TurnResult(
                resposta_cidadao="O serviço sugerido não está mais disponível.",
                acao_ui=None,
                cancelar_servico_pendente=True,
            )

        return TurnResult(
            resposta_cidadao=(
                f"Só para confirmar: o serviço é **{servico.nome}**. "
                "Responda Sim para continuar ou Não para escolher outro."
            ),
            acao_ui="confirmar_servico",
        )

    def _estagio_classificacao(self, sessao: SessaoChat, *, texto_usuario: str) -> TurnResult:
        candidatos = _servicos_candidatos(sessao)
        if not candidatos:
            return TurnResult(
                resposta_cidadao="Não há serviços ativos nesta categoria no momento.",
                acao_ui=None,
            )

        permitidos = {str(s.id) for s in candidatos}
        externos = _servicos_outras_categorias(sessao)
        todos_permitidos = {str(s.id) for s in ServicoCatalogo.objects.filter(ativo=True, is_template=False)}
        mensagens = _prepend_tom_llm(
            [
                {"role": "system", "content": SYSTEM_PROMPT_BASE},
                {
                    "role": "system",
                    "content": (
                        "Etapa A — Classificação.\n"
                        f"Categoria inicial do cidadão: {sessao.categoria_inicial}.\n"
                        f"Serviços desta categoria: {_catalogo_para_prompt(candidatos)}\n"
                        f"Serviços de outras categorias (se o relato indicar outro tipo de demanda): "
                        f"{_catalogo_para_prompt(externos)}\n"
                        "Se o melhor encaixe for desta categoria e confiança >= 0.7, retorne servico_id "
                        "e acao_ui=confirmar_servico. Se o melhor encaixe for de outra categoria, "
                        "retorne o servico_id correto com confiança >= 0.8 e explique na resposta_cidadao."
                    ),
                },
                *_historico(sessao),
                {"role": "user", "content": texto_usuario or "(sem texto)"},
            ],
            None,
        )

        parsed = _chamar_json_estruturado(
            nome_schema="classificacao_intencao",
            schema=CLASSIFICACAO_INTENCAO_SCHEMA,
            mensagens=mensagens,
            strict=True,
        )

        raw_sid = (parsed.get("servico_id") or "").strip()
        servico_id = _validar_servico_id(raw_sid, permitidos)
        servico_fora = _validar_servico_id(raw_sid, todos_permitidos) if raw_sid else None
        confianca = float(parsed.get("confianca") or 0)
        acao = _normalizar_acao(parsed.get("acao_ui"))
        resposta = (parsed.get("resposta_cidadao") or "").strip()
        meta = get_meta(sessao)

        if (
            not servico_id
            and servico_fora
            and confianca >= 0.8
            and not meta.get("forcar_categoria_atual")
            and meta.get("troca_categoria_recusada") != servico_fora
        ):
            try:
                srv_ext = ServicoCatalogo.objects.select_related("categoria").get(
                    pk=servico_fora, ativo=True, is_template=False
                )
            except ServicoCatalogo.DoesNotExist:
                srv_ext = None
            if srv_ext:
                motivo = resposta or (
                    f"Pelo que você descreveu, parece combinar mais com «{srv_ext.nome}» "
                    f"({srv_ext.categoria.nome if srv_ext.categoria_id else 'outra área'})."
                )
                payload = _montar_payload_troca_categoria(
                    sessao,
                    srv_ext,
                    mensagem_original=texto_usuario,
                    motivo=motivo,
                )
                set_meta(sessao, troca_categoria_pendente=payload)
                texto_ui = (
                    f"{motivo}\n\n"
                    "Posso direcionar para o serviço mais adequado, ou você pode continuar na categoria atual."
                )
                return TurnResult(
                    resposta_cidadao=texto_ui,
                    acao_ui="sugerir_troca_categoria",
                    payload_ui=payload,
                )

        if servico_id and confianca >= 0.7:
            return TurnResult(
                resposta_cidadao=resposta or "Identifiquei o serviço. Você confirma?",
                acao_ui=acao or "confirmar_servico",
                servico_pendente_id=UUID(servico_id),
                confirmar_servico=True,
            )

        return TurnResult(
            resposta_cidadao=resposta or "Conte mais detalhes para eu identificar o serviço correto.",
            acao_ui=acao,
        )

    def _extrair_dados_mensagem(
        self,
        sessao: SessaoChat,
        servico: ServicoCatalogo,
        texto_usuario: str,
        dados_atuais: dict,
    ) -> tuple[dict, bool]:
        faltantes = _campos_faltantes(servico, dados_atuais, sessao)
        campo_foco = faltantes[0] if faltantes else None
        opcional_foco = campo_foco and _campo_e_opcional(servico, campo_foco)
        schema_txt = _schema_resumido_para_prompt(servico.schema_formulario)
        mensagens = [
            {
                "role": "system",
                "content": (
                    "Você é um extrator de dados. Extraia da mensagem do usuário apenas "
                    "valores que correspondam ao schema do formulário. "
                    "Retorne JSON com dados_extraidos e intencao_pular (boolean). "
                    "intencao_pular=true quando o cidadão não sabe / não tem / quer pular campo opcional. "
                    "Não gere texto conversacional. "
                    "Para enums, use os valores canônicos do schema (ex.: pequeno, medio, grande). "
                    "Se o usuário responder com rótulo amigável, mapeie para o valor enum. "
                    "Não inclua campos vazios ou não mencionados."
                ),
            },
            {
                "role": "system",
                "content": (
                    f"Schema: {schema_txt}\n"
                    f"Dados já coletados: {json.dumps(dados_atuais, ensure_ascii=False)}\n"
                    f"Campos ainda faltantes (priorize estes): {faltantes}"
                    + (
                        f"\nCampo em foco agora: {campo_foco} ({'opcional' if opcional_foco else 'obrigatório'})."
                        if campo_foco
                        else ""
                    )
                ),
            },
            {"role": "user", "content": texto_usuario},
        ]
        parsed = _chamar_json_estruturado(
            nome_schema="extracao_dados",
            schema=EXTRACAO_DADOS_SCHEMA,
            mensagens=mensagens,
            strict=False,
        )
        bruto = parsed.get("dados_extraidos") if isinstance(parsed.get("dados_extraidos"), dict) else {}
        intencao_pular = bool(parsed.get("intencao_pular")) and bool(opcional_foco)
        return _filtrar_extraidos(bruto), intencao_pular

    def passo_deterministico_preenchimento(
        self,
        sessao: SessaoChat,
        *,
        dados_extraidos: dict | None = None,
        anexos_novos: int = 0,
        repescagem: bool = False,
    ) -> TurnResult:
        """Calcula o próximo passo (pergunta/UI) sem chamar LLM para redigir fluxo."""
        servico = sessao.servico_identificado
        if not servico:
            return TurnResult(
                resposta_cidadao="Preciso identificar o serviço antes de continuar.",
                acao_ui=None,
            )

        higienizar_lookup_na_sessao(sessao)
        from atendimentos.slot_filling_service import aplicar_equipamento_rede_seguranca_sessao

        aplicar_equipamento_rede_seguranca_sessao(sessao)
        sessao.refresh_from_db()

        dados_atuais = _dados_negocio(sessao)
        qtd_anexos = _qtd_anexos(sessao)
        extraidos_ret = _sanitizar_extraidos_campos_especiais(
            servico, dados_extraidos, sessao
        )
        merged = _sincronizar_campos_geo_imagem(
            sessao,
            servico,
            {**dados_atuais, **extraidos_ret},
            qtd_anexos=qtd_anexos,
        )

        bloqueio, motivo = _avaliar_regras_elegibilidade_detalhe(servico, merged)
        if bloqueio:
            return TurnResult(
                resposta_cidadao=bloqueio,
                acao_ui=None,
                dados_extraidos=extraidos_ret or None,
                fluxo_bloqueado=True,
                limpar_config_escolha=True,
                motivo_inelegibilidade=motivo,
            )

        faltantes = _campos_faltantes(servico, merged, sessao)
        loc_ok = _localizacao_ok(sessao)
        tem_campo_geo = _schema_tem_campo_tipo(servico, "geolocation")

        if faltantes:
            campo = faltantes[0]
            config = _montar_config_escolha(servico, campo)
            historico = _resumo_historico_sandbox(sessao)
            return TurnResult(
                resposta_cidadao=_pergunta_para_campo(
                    servico,
                    campo,
                    repescagem=repescagem,
                    historico_resumo=historico,
                ),
                acao_ui=_acao_ui_para_campo(servico, campo),
                dados_extraidos=extraidos_ret or None,
                config_escolha=config,
                limpar_config_escolha=config is None,
            )

        if servico.exige_localizacao and not loc_ok and not tem_campo_geo:
            return TurnResult(
                resposta_cidadao=_msg_localizacao_servico(servico),
                acao_ui="solicitar_localizacao",
                dados_extraidos=extraidos_ret or None,
                limpar_config_escolha=True,
            )

        if (
            _anexo_sessao_obrigatorio(sessao, servico)
            and anexos_novos < 1
        ):
            return TurnResult(
                resposta_cidadao=_msg_foto_servico(servico),
                acao_ui="solicitar_foto",
                dados_extraidos=extraidos_ret or None,
                limpar_config_escolha=True,
            )

        if _dados_completos(servico, merged, sessao):
            return TurnResult(
                resposta_cidadao=MSG_REVISAO,
                acao_ui="revisao_final",
                dados_extraidos=extraidos_ret or None,
                ir_para_revisao=True,
                limpar_config_escolha=True,
            )

        return TurnResult(
            resposta_cidadao="Conte um pouco mais sobre o que você precisa.",
            acao_ui=None,
            dados_extraidos=extraidos_ret or None,
            limpar_config_escolha=True,
        )

    def _estagio_slot_filling(
        self,
        sessao: SessaoChat,
        *,
        texto_usuario: str,
        anexos_novos: int,
        dados_slot: dict | None = None,
    ) -> TurnResult:
        servico = sessao.servico_identificado
        dados_atuais = _dados_negocio(sessao)
        extraidos: dict = dict(_filtrar_extraidos(dados_slot))

        repescagem = False
        campo_foco: str | None = None
        if not extraidos and _deve_extrair_texto(texto_usuario):
            faltantes = _campos_faltantes(servico, dados_atuais, sessao)
            if faltantes:
                campo_foco = faltantes[0]
                binario = _extrair_resposta_binaria_campo(
                    servico, campo_foco, texto_usuario
                )
                if binario is not None:
                    extraidos = {campo_foco: binario}
                elif _pular_opcional_se_declinio(
                    sessao, servico, campo_foco, texto_usuario
                ):
                    sessao.refresh_from_db()
                    turno = self.passo_deterministico_preenchimento(
                        sessao,
                        anexos_novos=anexos_novos,
                    )
                    if turno.resposta_cidadao:
                        turno.resposta_cidadao = (
                            f"{MSG_CAMPO_PULADO}\n\n{turno.resposta_cidadao}"
                        )
                    else:
                        turno.resposta_cidadao = MSG_CAMPO_PULADO
                    return turno
                from atendimentos.services.chat_equipamento_lookup import (
                    aplicar_equipamento_em_texto_usuario,
                )

                prop0 = _propriedade_campo(servico, campo_foco)
                ds = (prop0.get("x-ouvia-datasource") or "").strip()
                if ds == LOOKUP_DATASOURCE_EQUIPAMENTOS and texto_usuario.strip():
                    eq_extra = aplicar_equipamento_em_texto_usuario(
                        sessao, servico, texto_usuario
                    )
                    if eq_extra:
                        extraidos.update(eq_extra)
                        from atendimentos.lookup_campos import texto_lookup_nao_catalogado

                        for val in eq_extra.values():
                            nome_eq = texto_lookup_nao_catalogado(val) or ""
                            if nome_eq:
                                msg_eq = (
                                    f"Anotei {nome_eq} na sua solicitação para "
                                    "encaminhamento interno."
                                )
                                turno = self.passo_deterministico_preenchimento(
                                    sessao,
                                    dados_extraidos=eq_extra,
                                    anexos_novos=anexos_novos,
                                )
                                turno.resposta_cidadao = (
                                    f"{msg_eq}\n\n{turno.resposta_cidadao or ''}"
                                ).strip()
                                return turno
                intencao_pular = False
                if not extraidos and _tipo_ui_campo(prop0) not in ("geolocation", "image"):
                    try:
                        extraidos, intencao_pular = self._extrair_dados_mensagem(
                            sessao, servico, texto_usuario, dados_atuais
                        )
                    except ChatOrchestrationError:
                        logger.warning("Falha na extração; seguindo com dados atuais apenas.")
                        extraidos = {}
                        intencao_pular = False
                    if _pular_opcional_se_declinio(
                        sessao,
                        servico,
                        campo_foco,
                        texto_usuario,
                        intencao_pular_llm=intencao_pular,
                    ):
                        sessao.refresh_from_db()
                        turno = self.passo_deterministico_preenchimento(
                            sessao,
                            anexos_novos=anexos_novos,
                        )
                        turno.resposta_cidadao = (
                            f"{MSG_CAMPO_PULADO}\n\n{turno.resposta_cidadao or ''}"
                        ).strip()
                        return turno
                    extraidos = _remover_declinio_disfarcado_extraidos(sessao, servico, extraidos)
                    extraidos_limpos = _sanitizar_extraidos_campos_especiais(
                        servico,
                        extraidos,
                        sessao,
                        texto_usuario=texto_usuario,
                    )
                    repescagem = _deve_repescar_campo(
                        servico,
                        campo_foco,
                        texto_usuario,
                        extraidos_limpos,
                        sessao,
                    )
                    extraidos = extraidos_limpos
            extraidos = _sanitizar_extraidos_campos_especiais(
                servico, extraidos, sessao, texto_usuario=texto_usuario
            )
        elif extraidos:
            extraidos = _sanitizar_extraidos_campos_especiais(
                servico, extraidos, sessao, texto_usuario=texto_usuario
            )

        return self.passo_deterministico_preenchimento(
            sessao,
            dados_extraidos=extraidos,
            anexos_novos=anexos_novos,
            repescagem=repescagem,
        )

    def simular_turno_catalogo_sandbox(
        self,
        sessao_sandbox,
        *,
        texto_usuario: str = "",
        dados_slot: dict | None = None,
        anexos_novos: int = 0,
    ) -> TurnResult:
        """Dry-run: mesmo motor de produção, contexto em memória (``SessaoSandbox``)."""
        from atendimentos.chat_escolhas import normalizar_dados_slot

        servico = sessao_sandbox.servico_identificado
        dados_atuais = _dados_negocio(sessao_sandbox)
        extraidos: dict = dict(_filtrar_extraidos(dados_slot))

        if dados_slot:
            if dados_slot.get("__pular_campo"):
                from atendimentos.chat_estado import registrar_campo_pulado

                registrar_campo_pulado(sessao_sandbox, str(dados_slot.get("__pular_campo")).strip())
            slot_bruto = {k: v for k, v in dados_slot.items() if k != "__pular_campo"}
            if slot_bruto:
                slot = normalizar_dados_slot(servico, slot_bruto)
                extraidos = dict(_filtrar_extraidos(slot))
            elif dados_slot.get("__pular_campo"):
                turno = self.passo_deterministico_preenchimento(
                    sessao_sandbox,
                    anexos_novos=anexos_novos,
                )
                turno = _prefixar_resposta_campo_pulado(turno)
                return turno

        repescagem = False
        if not extraidos and _deve_extrair_texto(texto_usuario):
            faltantes = _campos_faltantes(servico, dados_atuais, sessao_sandbox)
            if faltantes:
                campo_foco = faltantes[0]
                binario = _extrair_resposta_binaria_campo(
                    servico, campo_foco, texto_usuario
                )
                if binario is not None:
                    extraidos = {campo_foco: binario}
                elif _pular_opcional_se_declinio(
                    sessao_sandbox, servico, campo_foco, texto_usuario
                ):
                    turno = self.passo_deterministico_preenchimento(
                        sessao_sandbox,
                        anexos_novos=anexos_novos,
                    )
                    return _prefixar_resposta_campo_pulado(turno)
                prop0 = _propriedade_campo(servico, campo_foco)
                tipo_ui_foco = _tipo_ui_campo(prop0)
                if not extraidos and tipo_ui_foco == "image":
                    if _pular_opcional_se_declinio(
                        sessao_sandbox, servico, campo_foco, texto_usuario
                    ):
                        turno = self.passo_deterministico_preenchimento(
                            sessao_sandbox,
                            anexos_novos=anexos_novos,
                        )
                        return _prefixar_resposta_campo_pulado(turno)
                if not extraidos and tipo_ui_foco not in ("geolocation", "image"):
                    intencao_pular = False
                    try:
                        extraidos, intencao_pular = self._extrair_dados_mensagem(
                            sessao_sandbox, servico, texto_usuario, dados_atuais
                        )
                    except ChatOrchestrationError:
                        extraidos = {}
                        intencao_pular = False
                    if _pular_opcional_se_declinio(
                        sessao_sandbox,
                        servico,
                        campo_foco,
                        texto_usuario,
                        intencao_pular_llm=intencao_pular,
                    ):
                        turno = self.passo_deterministico_preenchimento(
                            sessao_sandbox,
                            anexos_novos=anexos_novos,
                        )
                        return _prefixar_resposta_campo_pulado(turno)
                    extraidos = _remover_declinio_disfarcado_extraidos(
                        sessao_sandbox, servico, extraidos
                    )
                    extraidos_limpos = _sanitizar_extraidos_campos_especiais(
                        servico,
                        extraidos,
                        sessao_sandbox,
                        texto_usuario=texto_usuario,
                    )
                    repescagem = _deve_repescar_campo(
                        servico,
                        campo_foco,
                        texto_usuario,
                        extraidos_limpos,
                        sessao_sandbox,
                    )
                    extraidos = extraidos_limpos
            extraidos = _sanitizar_extraidos_campos_especiais(
                servico, extraidos, sessao_sandbox, texto_usuario=texto_usuario
            )
        elif extraidos:
            extraidos = _sanitizar_extraidos_campos_especiais(
                servico, extraidos, sessao_sandbox, texto_usuario=texto_usuario
            )

        turno = self.passo_deterministico_preenchimento(
            sessao_sandbox,
            dados_extraidos=extraidos or None,
            anexos_novos=anexos_novos,
            repescagem=repescagem,
        )
        if extraidos:
            from atendimentos.chat_sandbox import mesclar_dados_sandbox

            mesclar_dados_sandbox(sessao_sandbox, extraidos)
        return turno

    def _estagio_revisao(self, sessao: SessaoChat, *, texto_usuario: str) -> TurnResult:
        texto = (texto_usuario or "").strip()
        if texto and not confirmacao_protocolo_usuario(texto):
            servico = sessao.servico_identificado
            dados_atuais = _dados_negocio(sessao)
            repescagem = False
            try:
                extraidos, _ = self._extrair_dados_mensagem(
                    sessao, servico, texto, dados_atuais
                )
            except ChatOrchestrationError:
                extraidos = {}
            extraidos = _sanitizar_extraidos_campos_especiais(
                servico, extraidos, sessao, texto_usuario=texto
            )
            faltantes = _campos_faltantes(servico, dados_atuais, sessao)
            if faltantes:
                repescagem = _deve_repescar_campo(
                    servico, faltantes[0], texto, extraidos, sessao
                )
            passo = self.passo_deterministico_preenchimento(
                sessao,
                dados_extraidos=extraidos,
                anexos_novos=0,
                repescagem=repescagem,
            )
            if not passo.ir_para_revisao:
                set_meta(sessao, fase=FaseChat.PREENCHIMENTO)
                sessao.save(update_fields=["dados_coletados", "atualizado_em"])
            return passo

        return TurnResult(
            resposta_cidadao=MSG_REVISAO,
            acao_ui="revisao_final",
            ir_para_revisao=True,
        )


# Compatibilidade
avaliar_pronto_protocolo = avaliar_pronto_revisao
