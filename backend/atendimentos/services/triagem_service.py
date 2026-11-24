"""Motor de triagem (determinística + semântica LLM) — sugestões para a Mesa, sem auto-despacho."""

from __future__ import annotations

import json
import logging
import re
import uuid
from typing import Any

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from catalogo.datasources import LOOKUP_DATASOURCE_UNIDADES
from catalogo.equipamento_utils import campos_equipamentos_publicos_schema
from catalogo.models import MatrizRoteamentoTematico, ServicoCatalogo, UnidadeAdministrativa
from atendimentos.services.equipamento_protocolo import obter_equipamento_ativo
from atendimentos.models import MensagemChat, Protocolo

logger = logging.getLogger(__name__)

VERSAO_MOTOR = "deterministico_v1"
VERSAO_MOTOR_HIBRIDO = "hibrido_llm_v1"
FONTE_LOOKUP = "lookup_cidadao"
FONTE_MATRIZ = "matriz_eixo"
FONTE_EQUIPAMENTO = "equipamento_publico"
FONTE_CATALOGO_EXECUTOR = "catalogo_executor_padrao"
FONTE_LLM = "llm"
FONTES_DETERMINISTICAS = frozenset(
    {FONTE_LOOKUP, FONTE_MATRIZ, FONTE_EQUIPAMENTO, FONTE_CATALOGO_EXECUTOR}
)
CONFIANCA_EXECUTOR_PADRAO = 0.95
CONFIANCA_LOOKUP = 1.0
CONFIANCA_MATRIZ = 0.85
CONFIANCA_MINIMA_LLM = 0.50
MAX_UNIDADES_LLM = 3

_CHAVES_PII = frozenset(
    {
        "cpf",
        "cnpj",
        "telefone",
        "celular",
        "whatsapp",
        "email",
        "e_mail",
        "rg",
        "nome",
        "nome_cidadao",
        "nome_completo",
        "documento",
    }
)

TRIAGEM_SEMANTICA_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "unidades": {
            "type": "array",
            "maxItems": MAX_UNIDADES_LLM,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "confianca": {"type": "number"},
                    "motivo": {"type": "string"},
                },
                "required": ["id", "confianca", "motivo"],
                "additionalProperties": False,
            },
        },
        "resumo_motivo": {"type": "string"},
    },
    "required": ["unidades", "resumo_motivo"],
    "additionalProperties": False,
}


def _parse_uuid(valor: Any) -> uuid.UUID | None:
    if valor is None:
        return None
    try:
        return uuid.UUID(str(valor).strip())
    except (ValueError, TypeError, AttributeError):
        return None


def _campos_lookup_unidades(schema: dict | None) -> list[str]:
    from catalogo.equipamento_utils import campos_schema_datasource

    return campos_schema_datasource(schema, LOOKUP_DATASOURCE_UNIDADES)


def _registrar_sugestao(
    acumulado: dict[str, dict[str, Any]],
    unidade: UnidadeAdministrativa,
    *,
    confianca: float,
    fonte: str,
    motivo: str,
) -> None:
    chave = str(unidade.id)
    entrada = {
        "id": chave,
        "nome": unidade.nome,
        "confianca": confianca,
        "fonte": fonte,
        "motivo": motivo,
    }
    if chave in acumulado and acumulado[chave]["confianca"] >= confianca:
        return
    acumulado[chave] = entrada


def montar_triagem_sugerida(protocolo: Protocolo) -> dict[str, Any]:
    """Calcula payload ``triagem_sugerida`` sem persistir."""
    servico = protocolo.servico
    if servico.fluxo_tramitacao == ServicoCatalogo.FluxoTramitacao.DIRETO_SECRETARIA:
        return {}

    fluxo_encaminha = (
        servico.fluxo_tramitacao
        == ServicoCatalogo.FluxoTramitacao.OUVIDORIA_ENCAMINHA
    )
    if not fluxo_encaminha:
        return {}

    dados = protocolo.dados_dinamicos or {}
    schema = servico.schema_formulario or {}
    sugestoes: dict[str, dict[str, Any]] = {}

    executor_padrao = getattr(servico, "executor_padrao", None)
    if (
        executor_padrao
        and executor_padrao.ativo
        and servico.fluxo_tramitacao
        == ServicoCatalogo.FluxoTramitacao.OUVIDORIA_ENCAMINHA
    ):
        _registrar_sugestao(
            sugestoes,
            executor_padrao,
            confianca=CONFIANCA_EXECUTOR_PADRAO,
            fonte=FONTE_CATALOGO_EXECUTOR,
            motivo=f"Executor padrão do serviço: {servico.nome}",
        )

    equipamento = getattr(protocolo, "equipamento", None)
    if equipamento and equipamento.ativo and equipamento.unidade_responsavel.ativo:
        _registrar_sugestao(
            sugestoes,
            equipamento.unidade_responsavel,
            confianca=CONFIANCA_LOOKUP,
            fonte=FONTE_EQUIPAMENTO,
            motivo=f"Equipamento vinculado: {equipamento.nome}",
        )

    for chave in campos_equipamentos_publicos_schema(schema):
        eid = _parse_uuid(dados.get(chave))
        if not eid:
            continue
        eq = obter_equipamento_ativo(eid)
        if not eq:
            continue
        _registrar_sugestao(
            sugestoes,
            eq.unidade_responsavel,
            confianca=CONFIANCA_LOOKUP,
            fonte=FONTE_EQUIPAMENTO,
            motivo=f"Equipamento informado: {eq.nome}",
        )

    for chave in _campos_lookup_unidades(schema):
        uid = _parse_uuid(dados.get(chave))
        if not uid:
            continue
        unidade = UnidadeAdministrativa.objects.filter(pk=uid, ativo=True).first()
        if not unidade:
            continue
        _registrar_sugestao(
            sugestoes,
            unidade,
            confianca=CONFIANCA_LOOKUP,
            fonte=FONTE_LOOKUP,
            motivo=f"Cidadão informou «{chave}» ({unidade.nome}).",
        )

    regras = (
        MatrizRoteamentoTematico.objects.filter(servico=servico, ativo=True)
        .select_related("unidade_sugerida")
        .order_by("chave_schema", "valor_condicao")
    )
    for regra in regras:
        valor_campo = dados.get(regra.chave_schema)
        if valor_campo is None:
            continue
        if str(valor_campo).strip() != str(regra.valor_condicao).strip():
            continue
        unidade = regra.unidade_sugerida
        if not unidade.ativo:
            continue
        _registrar_sugestao(
            sugestoes,
            unidade,
            confianca=CONFIANCA_MATRIZ,
            fonte=FONTE_MATRIZ,
            motivo=f"Regra {regra.chave_schema}={regra.valor_condicao}",
        )

    lista = sorted(sugestoes.values(), key=lambda item: (-item["confianca"], item["nome"]))
    if not lista:
        return {}

    return {
        "unidades_sugeridas": lista,
        "gerada_em": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "versao_motor": VERSAO_MOTOR,
    }


def _acumulado_de_payload(triagem: dict | None) -> dict[str, dict[str, Any]]:
    acumulado: dict[str, dict[str, Any]] = {}
    for item in (triagem or {}).get("unidades_sugeridas") or []:
        uid = item.get("id")
        if uid:
            acumulado[str(uid)] = dict(item)
    return acumulado


def _incorporar_sugestao(
    acumulado: dict[str, dict[str, Any]],
    entrada: dict[str, Any],
) -> None:
    """Merge com prioridade das fontes determinísticas (Onda 4)."""
    uid = str(entrada["id"])
    if uid in acumulado:
        ant = acumulado[uid]
        confianca = max(float(ant.get("confianca") or 0), float(entrada.get("confianca") or 0))
        fonte = ant.get("fonte") or entrada.get("fonte")
        motivo = (ant.get("motivo") or "").strip()
        if fonte in FONTES_DETERMINISTICAS:
            extra = (entrada.get("motivo") or "").strip()
            if extra and extra not in motivo:
                motivo = f"{motivo} · IA: {extra}" if motivo else extra
        else:
            if float(entrada.get("confianca") or 0) >= float(ant.get("confianca") or 0):
                fonte = entrada.get("fonte", fonte)
                motivo = entrada.get("motivo") or motivo
        acumulado[uid] = {
            "id": uid,
            "nome": ant.get("nome") or entrada.get("nome"),
            "confianca": confianca,
            "fonte": fonte,
            "motivo": motivo,
        }
        return
    acumulado[uid] = entrada


def _payload_de_acumulado(
    acumulado: dict[str, dict[str, Any]],
    *,
    versao_motor: str,
    resumo_motivo: str = "",
    versao_modelo: str = "",
    gerada_em: str | None = None,
) -> dict[str, Any]:
    lista = sorted(
        acumulado.values(),
        key=lambda item: (-float(item.get("confianca") or 0), item.get("nome") or ""),
    )
    if not lista and not (resumo_motivo or "").strip():
        return {}
    payload: dict[str, Any] = {
        "unidades_sugeridas": lista,
        "gerada_em": gerada_em or timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "versao_motor": versao_motor,
    }
    if (resumo_motivo or "").strip():
        payload["resumo_motivo"] = resumo_motivo.strip()
    if (versao_modelo or "").strip():
        payload["versao_modelo"] = versao_modelo.strip()
    return payload


def servico_elegivel_triagem_semantica(servico: ServicoCatalogo) -> bool:
    if not servico.triagem_ia_ativa:
        return False
    return (
        servico.fluxo_tramitacao
        == ServicoCatalogo.FluxoTramitacao.OUVIDORIA_ENCAMINHA
    )


def agendar_triagem_semantica_pos_deterministica(protocolo: Protocolo) -> None:
    """Enfileira LLM após commit da triagem determinística (sem bloquear criação do protocolo)."""
    servico = protocolo.servico
    if not servico_elegivel_triagem_semantica(servico):
        return

    protocolo_id = str(protocolo.pk)

    def _disparar() -> None:
        from atendimentos.tasks import executar_triagem_semantica_task

        executar_triagem_semantica_task.delay(protocolo_id)

    transaction.on_commit(_disparar)


def executar_triagem_protocolo(protocolo: Protocolo, *, persistir: bool = True) -> dict[str, Any]:
    """
    Gera e, opcionalmente, persiste sugestões para protocolos em fluxo de encaminhamento.
    Não altera status do protocolo (permanece em análise até despacho humano).
    """
    from atendimentos.services.equipamento_protocolo import sincronizar_equipamento_no_protocolo

    protocolo = (
        Protocolo.objects.select_related(
            "servico",
            "equipamento",
            "equipamento__unidade_responsavel",
        )
        .get(pk=protocolo.pk)
    )
    sincronizar_equipamento_no_protocolo(protocolo)

    payload = montar_triagem_sugerida(protocolo)
    if persistir:
        protocolo.triagem_sugerida = payload
        protocolo.save(update_fields=["triagem_sugerida", "data_atualizacao"])
        agendar_triagem_semantica_pos_deterministica(protocolo)
    return payload


def _dados_dinamicos_sem_pii(dados: dict | None) -> dict[str, Any]:
    limpo: dict[str, Any] = {}
    for chave, valor in (dados or {}).items():
        if str(chave).startswith("_"):
            continue
        if str(chave).lower() in _CHAVES_PII:
            continue
        if isinstance(valor, str) and re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", valor):
            continue
        limpo[chave] = valor
    return limpo


def _historico_chat_para_triagem(protocolo: Protocolo, limite: int = 8) -> list[dict[str, str]]:
    sessao = getattr(protocolo, "sessao_chat", None)
    if sessao is None:
        return []
    linhas: list[dict[str, str]] = []
    qs = sessao.mensagens.order_by("-criado_em")[:limite]
    for msg in reversed(list(qs)):
        papel = "cidadao" if msg.autor == MensagemChat.Autor.CIDADAO else "assistente"
        texto = (msg.conteudo_texto or "").strip()[:400]
        if texto:
            linhas.append({"papel": papel, "texto": texto})
    return linhas


def _catalogo_unidades_para_llm() -> list[dict[str, str]]:
    itens = []
    for unidade in UnidadeAdministrativa.objects.filter(ativo=True).order_by("nome"):
        escopo = (unidade.descricao or "").strip()
        if unidade.diretrizes_tom_ia:
            escopo = (
                f"{escopo} {unidade.diretrizes_tom_ia}".strip()
                if escopo
                else unidade.diretrizes_tom_ia.strip()
            )
        itens.append(
            {
                "id": str(unidade.id),
                "nome": unidade.nome,
                "escopo": escopo[:500],
            }
        )
    return itens


def _montar_contexto_llm(protocolo: Protocolo) -> dict[str, Any]:
    servico = protocolo.servico
    dados = _dados_dinamicos_sem_pii(protocolo.dados_dinamicos)
    return {
        "servico": servico.nome,
        "descricao_protocolo": (protocolo.descricao or "")[:1200],
        "dados_estruturados": dados,
        "mensagens_chat": _historico_chat_para_triagem(protocolo),
        "unidades_disponiveis": _catalogo_unidades_para_llm(),
    }


def _chamar_llm_triagem_semantica(contexto: dict[str, Any]) -> dict[str, Any]:
    from atendimentos.llm_orchestrator import ChatOrchestrationError, _chamar_json_estruturado, _modelo

    sistema = (
        "Você é analista de encaminhamento da Ouvidoria Municipal. "
        "Com base no relato e nos dados, sugira até 3 unidades executoras "
        "escolhendo APENAS ids do catálogo `unidades_disponiveis`. "
        "confianca entre 0.5 e 1.0. motivo em uma frase curta em português. "
        "resumo_motivo: uma frase sintetizando o encaminhamento sugerido."
    )
    mensagens = [
        {"role": "system", "content": sistema},
        {
            "role": "user",
            "content": json.dumps(contexto, ensure_ascii=False),
        },
    ]
    return _chamar_json_estruturado(
        nome_schema="triagem_semantica",
        schema=TRIAGEM_SEMANTICA_JSON_SCHEMA,
        mensagens=mensagens,
        strict=False,
    )


def _filtrar_sugestoes_llm(
    raw: dict[str, Any],
    unidades_ativas: dict[str, UnidadeAdministrativa],
) -> tuple[list[dict[str, Any]], str]:
    resumo = (raw.get("resumo_motivo") or "").strip()
    validadas: list[dict[str, Any]] = []
    for item in raw.get("unidades") or []:
        if not isinstance(item, dict):
            continue
        uid = _parse_uuid(item.get("id"))
        if not uid:
            continue
        chave = str(uid)
        unidade = unidades_ativas.get(chave)
        if not unidade:
            continue
        try:
            conf = float(item.get("confianca"))
        except (TypeError, ValueError):
            continue
        if conf < CONFIANCA_MINIMA_LLM:
            continue
        motivo = (item.get("motivo") or "").strip() or f"Sugestão semântica: {unidade.nome}"
        validadas.append(
            {
                "id": chave,
                "nome": unidade.nome,
                "confianca": round(min(conf, 1.0), 3),
                "fonte": FONTE_LLM,
                "motivo": motivo,
            }
        )
        if len(validadas) >= MAX_UNIDADES_LLM:
            break
    return validadas, resumo


def merge_triagem_com_llm(
    triagem_base: dict[str, Any],
    sugestoes_llm: list[dict[str, Any]],
    *,
    resumo_motivo: str = "",
    versao_modelo: str = "",
) -> dict[str, Any]:
    acumulado = _acumulado_de_payload(triagem_base)
    for entrada in sugestoes_llm:
        _incorporar_sugestao(acumulado, entrada)
    resumo = (resumo_motivo or triagem_base.get("resumo_motivo") or "").strip()
    return _payload_de_acumulado(
        acumulado,
        versao_motor=VERSAO_MOTOR_HIBRIDO,
        resumo_motivo=resumo,
        versao_modelo=versao_modelo,
        gerada_em=triagem_base.get("gerada_em"),
    )


def executar_triagem_semantica_llm(protocolo_id: str | uuid.UUID) -> dict[str, Any] | None:
    """
    Enriquece ``triagem_sugerida`` com sugestões LLM (assíncrono).
    Em falha, preserva a triagem determinística já gravada.
    """
    try:
        protocolo = (
            Protocolo.objects.select_related("servico", "sessao_chat")
            .prefetch_related("sessao_chat__mensagens")
            .get(pk=protocolo_id)
        )
    except Protocolo.DoesNotExist:
        logger.warning("Triagem semântica: protocolo %s inexistente.", protocolo_id)
        return None

    servico = protocolo.servico
    if not servico_elegivel_triagem_semantica(servico):
        return protocolo.triagem_sugerida or {}

    triagem_base = dict(protocolo.triagem_sugerida or {})

    api_key = (getattr(settings, "LLM_CHAT_API_KEY", "") or "").strip()
    if not api_key:
        logger.warning(
            "Triagem semântica ignorada (LLM não configurado) — protocolo %s.",
            protocolo.codigo,
        )
        return triagem_base

    unidades_map = {
        str(u.id): u
        for u in UnidadeAdministrativa.objects.filter(ativo=True).only(
            "id", "nome", "descricao", "diretrizes_tom_ia"
        )
    }

    try:
        from atendimentos.llm_orchestrator import ChatOrchestrationError, _modelo

        contexto = _montar_contexto_llm(protocolo)
        resposta = _chamar_llm_triagem_semantica(contexto)
        sugestoes, resumo = _filtrar_sugestoes_llm(resposta, unidades_map)
        versao_modelo = _modelo()
    except Exception as exc:
        from atendimentos.llm_orchestrator import ChatOrchestrationError as _ChatOrchestrationError

        logger.warning(
            "Triagem semântica falhou para %s: %s",
            protocolo.codigo,
            exc,
            exc_info=not isinstance(exc, _ChatOrchestrationError),
        )
        return triagem_base

    if not sugestoes and not resumo:
        return triagem_base

    merged = merge_triagem_com_llm(
        triagem_base,
        sugestoes,
        resumo_motivo=resumo,
        versao_modelo=versao_modelo,
    )
    if not merged:
        return triagem_base

    protocolo.triagem_sugerida = merged
    protocolo.save(update_fields=["triagem_sugerida", "data_atualizacao"])
    return merged


def texto_auditoria_despacho_triagem(
    protocolo: Protocolo, unidade_ids_despachadas: list
) -> str:
    """Texto para histórico: confirmação ou divergência em relação à triagem sugerida."""
    triagem = protocolo.triagem_sugerida or {}
    sugeridas = triagem.get("unidades_sugeridas") or []
    if not sugeridas:
        return ""

    ids_sugeridos = {item["id"] for item in sugeridas if item.get("id")}
    ids_despacho = {str(uid) for uid in unidade_ids_despachadas}
    if not ids_despacho:
        return ""

    confirmados = ids_despacho & ids_sugeridos
    divergentes = ids_despacho - ids_sugeridos

    partes: list[str] = ["Auditoria de triagem:"]
    if confirmados:
        nomes = [
            next((s["nome"] for s in sugeridas if s["id"] == uid), uid)
            for uid in sorted(confirmados)
        ]
        partes.append(
            f"confirmou sugestão para {', '.join(nomes)}."
        )
    if divergentes:
        partes.append(
            f"divergiu da sugestão ao incluir unidade(s) não sugeridas "
            f"({len(divergentes)} id(s))."
        )
    if not confirmados and divergentes:
        partes = [
            "Auditoria de triagem: despacho não coincide com nenhuma unidade sugerida "
            f"({len(ids_sugeridos)} sugestão(ões) ignorada(s))."
        ]
    return " ".join(partes)