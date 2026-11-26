"""Orquestrador do Copiloto Gestor — seleção de tools, síntese LLM e guardrails."""

from __future__ import annotations

import json
import logging
from typing import Any

from django.utils import timezone

from atendimentos.models import (
    ConfiguracaoAgenteGestao,
    MensagemCopilotoGestor,
    SessaoCopilotoGestor,
)
from atendimentos.services.agente_briefing_service import (
    _GLOSSARIO_DOMINIO,
    _sanitizar_gramatica_pt,
    obter_consumo_tokens_mes,
)
from atendimentos.services.agente_copiloto_tools import (
    NOMES_TOOLS,
    catalogo_tools_llm,
    executar_tool,
)
from atendimentos.services.agente_persona import resolver_escopo_briefing_usuario
from catalogo.models import UnidadeAdministrativa

logger = logging.getLogger(__name__)

# Schemas enxutos — Groq/OpenAI rejeitam objetos aninhados sem additionalProperties (erro 400).
TOOL_SELECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "tools": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string"},
                },
                "required": ["nome"],
            },
        },
    },
    "required": ["tools"],
}

SINTESE_SCHEMA = {
    "type": "object",
    "properties": {
        "resposta": {"type": "string"},
    },
    "required": ["resposta"],
}


def _compactar_resultados_para_llm(resultados_tools: list[dict]) -> list[dict]:
    """Reduz payload enviado ao LLM (evita falha de validação e estouro de contexto)."""
    out: list[dict] = []
    for bloco in resultados_tools:
        dados = dict(bloco.get("dados") or {})
        dados.pop("referencias_candidatas", None)
        for chave in (
            "protocolos",
            "ranking_atraso_secretarias",
            "equipamentos_anomalia",
            "bairros_anomalia",
            "por_secretaria",
            "por_servico",
        ):
            if isinstance(dados.get(chave), list):
                dados[chave] = dados[chave][:8]
        out.append({"tool": bloco.get("tool"), "dados": dados})
    return out


def truncar_titulo_sessao(pergunta: str, max_len: int = 140) -> str:
    t = " ".join((pergunta or "").split())
    if len(t) <= max_len:
        return t or "Nova conversa"
    cortado = t[:max_len].rsplit(" ", 1)[0].strip()
    return cortado or t[:max_len]


def contar_perguntas_hoje(usuario) -> int:
    return MensagemCopilotoGestor.objects.filter(
        sessao__usuario=usuario,
        papel=MensagemCopilotoGestor.Papel.USUARIO,
        criado_em__date=timezone.localdate(),
    ).count()


def verificar_copiloto_disponivel(usuario) -> tuple[bool, str | None]:
    cfg = ConfiguracaoAgenteGestao.load()
    if not cfg.agente_ativo:
        return False, "Agente de gestão desativado pelo administrador."
    if not cfg.copiloto_chat_ativo:
        return False, "Copiloto em chat está desativado."
    return True, None


def budget_esgotado() -> bool:
    cfg = ConfiguracaoAgenteGestao.load()
    consumo = obter_consumo_tokens_mes()
    return consumo >= int(cfg.orcamento_tokens_mensal)


def _persona_instrucao(escopo_tipo: str) -> str:
    from atendimentos.services.agente_briefing_service import _persona_instrucao as _p

    return _p(escopo_tipo)


def sugestoes_iniciais(escopo_tipo: str, rota: str = "") -> list[str]:
    base = {
        "controladoria": [
            "Qual secretaria concentra mais atraso de SLA nos últimos 30 dias?",
            "Há picos territoriais ou em equipamentos públicos que exigem ação?",
            "Como está a taxa de retrabalho e o CSAT no município?",
        ],
        "ouvidoria": [
            "Quais gargalos de SLA e cobranças ao cidadão merecem prioridade?",
            "Quantas sugestões de urgência da IA ainda aguardam revisão?",
            "Resumo de inelegibilidade: quais serviços mais bloqueiam cidadãos?",
        ],
        "unidade": [
            "Foto da minha fila: análise parada, revisão e críticos sem OS.",
            "Liste protocolos vencidos ou com cobrança na minha secretaria.",
            "Há anomalias recentes por bairro ou equipamento na minha área?",
        ],
    }
    sugs = list(base.get(escopo_tipo, base["controladoria"]))
    if "mesa-trabalho" in rota:
        sugs[0] = "Resuma a fila operacional atual da Mesa de Trabalho."
    elif "eficiencia" in rota:
        sugs[0] = "Resumo de eficiência e TMA dos últimos 30 dias no meu escopo."
    elif "inelegibilidade" in rota:
        sugs[0] = "Por que cidadãos estão sendo barrados no chat e em quais serviços?"
    return sugs[:3]


def config_usuario_payload(usuario, rota: str = "") -> dict[str, Any]:
    escopo_tipo, unidade_id = resolver_escopo_briefing_usuario(usuario, {})
    unidade_nome = None
    if unidade_id:
        unidade_nome = (
            UnidadeAdministrativa.objects.filter(pk=unidade_id).values_list("nome", flat=True).first()
        )
    cfg = ConfiguracaoAgenteGestao.load()
    ok, motivo = verificar_copiloto_disponivel(usuario)
    perguntas = contar_perguntas_hoje(usuario)
    esgotado = budget_esgotado()
    return {
        "copiloto_disponivel": ok and not esgotado,
        "motivo_indisponivel": motivo if not ok else ("Orçamento mensal de IA esgotado." if esgotado else None),
        "perspectiva": escopo_tipo,
        "unidade_nome": unidade_nome,
        "perguntas_hoje": perguntas,
        "limite_diario": int(cfg.limite_perguntas_dia_por_usuario),
        "budget_esgotado": esgotado,
        "sugestoes_iniciais": sugestoes_iniciais(escopo_tipo, rota),
    }


def _historico_sem_pii(sessao: SessaoCopilotoGestor, limite: int = 4) -> list[dict]:
    msgs = list(sessao.mensagens.order_by("-criado_em")[: limite + 1])
    out = []
    for m in reversed(msgs):
        if m.status_processamento == MensagemCopilotoGestor.StatusProcessamento.PROCESSANDO:
            continue
        out.append({"papel": m.papel, "conteudo": (m.conteudo or "")[:800]})
    return out[-limite:]


def _classificar_intencao(pergunta: str) -> list[dict]:
    p = (pergunta or "").lower()
    tools: list[dict] = []
    if any(w in p for w in ("fila", "mesa", "triagem", "revisão", "revisao", "crítico", "critico")):
        tools.append({"nome": "resumir_fila_operacional", "parametros": {}})
    if any(w in p for w in ("sla", "vencido", "atraso", "cobrança", "cobranca", "gargalo")):
        tools.append({"nome": "listar_gargalos_sla_e_cobrancas", "parametros": {"limite": 10}})
    if any(w in p for w in ("eficiência", "eficiencia", "tma", "resolvido", "ranking")):
        tools.append({"nome": "obter_resumo_eficiencia", "parametros": {"periodo_dias": 30}})
    if any(w in p for w in ("bairro", "equipamento", "mapa", "território", "territorio", "anomalia", "pico")):
        tools.append({"nome": "listar_anomalias_equipamentos_bairros", "parametros": {"periodo_dias": 14}})
    if any(w in p for w in ("csat", "retrabalho", "reabert", "qualidade", "satisfação", "satisfacao")):
        tools.append({"nome": "obter_qualidade_e_retrabalho", "parametros": {"periodo_dias": 30}})
    if any(w in p for w in ("ineleg", "bloqueio", "chat", "cidadão barrado", "cidadao barrado")):
        tools.append({"nome": "obter_resumo_inelegibilidade", "parametros": {"periodo_dias": 30}})
    if not tools:
        tools.append({"nome": "resumir_fila_operacional", "parametros": {}})
    return tools[:3]


def _selecionar_tools_llm(
    pergunta: str,
    historico: list[dict],
    escopo_tipo: str,
    usage_sink: list,
) -> tuple[list[dict], int, int, str]:
    from atendimentos.llm_orchestrator import _chamar_json_estruturado, _modelo

    sistema = (
        "Você escolhe de 1 a 3 ferramentas (tools) somente leitura para responder ao gestor. "
        "Retorne JSON com lista 'tools': cada item tem 'nome' (exatamente um dos nomes do catálogo) "
        "e 'parametros' opcional. Não invente ferramentas."
    )
    user_payload = {
        "pergunta": pergunta,
        "historico": historico,
        "perspectiva": escopo_tipo,
        "catalogo": catalogo_tools_llm(),
    }
    mensagens = [
        {"role": "system", "content": sistema},
        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
    ]
    try:
        parsed = _chamar_json_estruturado(
            nome_schema="copiloto_tool_selection",
            schema=TOOL_SELECTION_SCHEMA,
            mensagens=mensagens,
            strict=False,
            usage_sink=usage_sink,
        )
        tools = parsed.get("tools") or []
        valid = []
        for t in tools:
            nome = (t.get("nome") or "").strip()
            if nome in NOMES_TOOLS:
                params = t.get("parametros") if isinstance(t.get("parametros"), dict) else {}
                valid.append({"nome": nome, "parametros": params or {}})
        if valid:
            modelo = _modelo()
            tin = int(usage_sink[0]) if len(usage_sink) >= 1 else 0
            tout = int(usage_sink[1]) if len(usage_sink) >= 2 else 0
            return valid[:3], tin, tout, modelo
    except Exception as exc:
        logger.warning("Seleção de tools LLM falhou: %s", exc)
    return _classificar_intencao(pergunta), 0, 0, ""


def _deduplicar_referencias(candidatas: list[dict], max_itens: int = 4) -> list[dict]:
    vistos = set()
    out = []
    for ref in candidatas:
        if not isinstance(ref, dict):
            continue
        chave = (ref.get("rota"), json.dumps(ref.get("query") or {}, sort_keys=True))
        if chave in vistos:
            continue
        vistos.add(chave)
        out.append(
            {
                "label": ref.get("label", "Abrir"),
                "tipo": ref.get("tipo", "navegacao"),
                "rota": ref.get("rota", "/backoffice/mesa-trabalho"),
                "query": ref.get("query") or {},
            }
        )
        if len(out) >= max_itens:
            break
    return out


def _sintese_llm(
    pergunta: str,
    escopo_tipo: str,
    resultados_tools: list[dict],
    usage_sink: list,
) -> tuple[str, int, int, str]:
    from atendimentos.llm_orchestrator import _chamar_json_estruturado, _modelo

    sistema = (
        "Você é o Copiloto analítico do backoffice municipal. Responda em português, tom executivo, "
        "em 2–5 parágrafos curtos. Use APENAS números e fatos do JSON de resultados. "
        "NÃO invente protocolos, links ou percentuais. NÃO cite CPF, nome, e-mail ou telefone de cidadãos. "
        "Mencione códigos PROT- apenas se estiverem no JSON. "
        "Oriente o gestor a usar os chips de navegação (referencias) para agir — você não executa ações. "
        f"{_GLOSSARIO_DOMINIO} "
        f"{_persona_instrucao(escopo_tipo)}"
    )
    payload = {
        "pergunta": pergunta,
        "resultados_tools": _compactar_resultados_para_llm(resultados_tools),
    }
    mensagens = [
        {"role": "system", "content": sistema},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False, default=str)},
    ]
    parsed = _chamar_json_estruturado(
        nome_schema="copiloto_sintese",
        schema=SINTESE_SCHEMA,
        mensagens=mensagens,
        strict=False,
        usage_sink=usage_sink,
    )
    modelo = _modelo()
    texto = _sanitizar_gramatica_pt((parsed.get("resposta") or "").strip()[:4000])
    tin = int(usage_sink[0]) if len(usage_sink) >= 1 else 0
    tout = int(usage_sink[1]) if len(usage_sink) >= 2 else 0
    return texto, tin, tout, modelo


def _resposta_deterministica(resultados_tools: list[dict], *, motivo: str = "budget") -> str:
    partes = []
    for bloco in resultados_tools:
        nome = bloco.get("tool")
        dados = bloco.get("dados") or {}
        if nome == "resumir_fila_operacional":
            partes.append(
                f"Fila operacional: {dados.get('total_itens_kanban', 0)} itens no Kanban; "
                f"{dados.get('em_analise', 0)} em análise; {dados.get('aguardando_revisao', 0)} aguardando revisão; "
                f"{dados.get('criticos_sem_os_abertos', 0)} críticos sem OS; "
                f"{dados.get('sugestoes_urgencia_ia_pendentes', 0)} sugestões de urgência IA pendentes."
            )
        elif nome == "obter_resumo_eficiencia":
            partes.append(
                f"Eficiência ({dados.get('periodo_dias')}d): {dados.get('total_abertos')} abertos, "
                f"{dados.get('total_resolvidos')} resolvidos; TMA médio {dados.get('tma_horas_medio')}h; "
                f"{dados.get('percentual_no_prazo_mesa')}% dos itens da mesa no prazo."
            )
        elif nome == "listar_gargalos_sla_e_cobrancas":
            protos = dados.get("protocolos") or []
            if protos:
                cods = ", ".join(p["codigo"] for p in protos[:5])
                partes.append(f"Gargalos SLA/cobrança: destaque para {cods}.")
            else:
                partes.append("Não há gargalos de SLA ou cobrança críticos no escopo consultado.")
        elif nome == "obter_resumo_inelegibilidade":
            partes.append(
                f"Inelegibilidade: {dados.get('total_sessoes_bloqueadas', 0)} sessões bloqueadas no período."
            )
        else:
            partes.append(f"Consulta «{nome}» concluída com dados agregados no escopo permitido.")
    if motivo == "budget":
        partes.append(
            "O orçamento mensal de IA foi atingido; esta resposta foi gerada de forma determinística. "
            "Use os atalhos abaixo para navegar e executar ações no sistema."
        )
    else:
        partes.append(
            "A síntese por IA não ficou disponível neste turno; os números acima vêm "
            "diretamente das consultas verificáveis no sistema. Use os atalhos abaixo para agir."
        )
    return "\n\n".join(partes)


def processar_mensagem_copiloto(mensagem_assistente_id: str) -> None:
    msg = MensagemCopilotoGestor.objects.select_related("sessao", "sessao__usuario", "sessao__unidade").get(
        pk=mensagem_assistente_id
    )
    if msg.papel != MensagemCopilotoGestor.Papel.ASSISTENTE:
        return
    sessao = msg.sessao
    usuario = sessao.usuario
    pergunta_msg = (
        sessao.mensagens.filter(papel=MensagemCopilotoGestor.Papel.USUARIO)
        .order_by("-criado_em")
        .first()
    )
    pergunta = (pergunta_msg.conteudo if pergunta_msg else "").strip()
    escopo_tipo = sessao.perspectiva

    tokens_in = 0
    tokens_out = 0
    modelo = ""
    ferramentas_log: list[dict] = []
    referencias: list[dict] = []
    modo = MensagemCopilotoGestor.ModoGeracao.FALLBACK

    try:
        if budget_esgotado():
            tools_sel = _classificar_intencao(pergunta)
        else:
            uso1: list = []
            tools_sel, t1, t2, modelo = _selecionar_tools_llm(
                pergunta,
                _historico_sem_pii(sessao),
                escopo_tipo,
                uso1,
            )
            tokens_in += t1
            tokens_out += t2
            if not tools_sel:
                tools_sel = _classificar_intencao(pergunta)

        resultados: list[dict] = []
        refs_cand: list[dict] = []
        for t in tools_sel:
            nome = t["nome"]
            params = dict(t.get("parametros") or {})
            if sessao.unidade_id and "unidade_id" not in params:
                params["unidade_id"] = str(sessao.unidade_id)
            dados = executar_tool(nome, usuario, params)
            resultados.append({"tool": nome, "dados": dados})
            ferramentas_log.append({"nome": nome, "parametros": params})
            refs_cand.extend((dados.get("referencias_candidatas") or []))

        referencias = _deduplicar_referencias(refs_cand)

        if budget_esgotado():
            conteudo = _resposta_deterministica(resultados, motivo="budget")
            modo = MensagemCopilotoGestor.ModoGeracao.FALLBACK
        else:
            uso2: list = []
            try:
                conteudo, t3, t4, modelo_s = _sintese_llm(pergunta, escopo_tipo, resultados, uso2)
                tokens_in += int(uso2[0]) if len(uso2) >= 1 else t3
                tokens_out += int(uso2[1]) if len(uso2) >= 2 else t4
                if modelo_s:
                    modelo = modelo_s
                modo = MensagemCopilotoGestor.ModoGeracao.LLM
                if not conteudo:
                    conteudo = _resposta_deterministica(resultados, motivo="llm")
                    modo = MensagemCopilotoGestor.ModoGeracao.FALLBACK
            except Exception as exc_sintese:
                logger.warning("Síntese Copiloto LLM falhou, fallback determinístico: %s", exc_sintese)
                conteudo = _resposta_deterministica(resultados, motivo="llm")
                modo = MensagemCopilotoGestor.ModoGeracao.FALLBACK

        msg.conteudo = conteudo
        msg.status_processamento = MensagemCopilotoGestor.StatusProcessamento.CONCLUIDA
        msg.ferramentas_usadas = ferramentas_log
        msg.referencias = referencias
        msg.modo_geracao = modo
        msg.modelo_llm = modelo or ""
        msg.tokens_entrada = tokens_in
        msg.tokens_saida = tokens_out
        msg.erro_detalhe = ""
        msg.save(
            update_fields=[
                "conteudo",
                "status_processamento",
                "ferramentas_usadas",
                "referencias",
                "modo_geracao",
                "modelo_llm",
                "tokens_entrada",
                "tokens_saida",
                "erro_detalhe",
            ]
        )
        sessao.save(update_fields=["atualizado_em"])
    except Exception as exc:
        logger.exception("Erro ao processar copiloto: %s", exc)
        msg.conteudo = (
            "Não foi possível concluir a análise neste momento. "
            "Tente reformular a pergunta ou aguarde alguns instantes."
        )
        msg.status_processamento = MensagemCopilotoGestor.StatusProcessamento.ERRO
        msg.erro_detalhe = "processamento_falhou"
        msg.save(
            update_fields=["conteudo", "status_processamento", "erro_detalhe"],
        )


def criar_sessao_ou_reusar(
    usuario,
    pergunta: str,
    sessao_id=None,
    contexto_rota: str = "",
) -> SessaoCopilotoGestor:
    escopo_tipo, unidade_id = resolver_escopo_briefing_usuario(usuario, {})
    if sessao_id:
        return SessaoCopilotoGestor.objects.get(pk=sessao_id, usuario=usuario)
    unidade = None
    if unidade_id:
        unidade = UnidadeAdministrativa.objects.filter(pk=unidade_id, ativo=True).first()
    return SessaoCopilotoGestor.objects.create(
        usuario=usuario,
        titulo=truncar_titulo_sessao(pergunta),
        perspectiva=escopo_tipo,
        unidade=unidade,
        contexto_rota_inicial=(contexto_rota or "")[:120],
    )


def montar_resposta_sessao(sessao: SessaoCopilotoGestor) -> dict[str, Any]:
    ia_proc = sessao.mensagens.filter(
        papel=MensagemCopilotoGestor.Papel.ASSISTENTE,
        status_processamento=MensagemCopilotoGestor.StatusProcessamento.PROCESSANDO,
    ).exists()
    mensagens = []
    for m in sessao.mensagens.order_by("criado_em"):
        mensagens.append(
            {
                "id": str(m.id),
                "papel": m.papel,
                "conteudo": m.conteudo,
                "status_processamento": m.status_processamento,
                "ferramentas_usadas": m.ferramentas_usadas,
                "referencias": m.referencias,
                "modo_geracao": m.modo_geracao,
                "modelo_llm": m.modelo_llm,
                "tokens_entrada": m.tokens_entrada,
                "tokens_saida": m.tokens_saida,
                "erro_detalhe": m.erro_detalhe,
                "criado_em": m.criado_em.isoformat(),
            }
        )
    return {
        "sessao_id": str(sessao.id),
        "titulo": sessao.titulo,
        "perspectiva": sessao.perspectiva,
        "unidade_id": str(sessao.unidade_id) if sessao.unidade_id else None,
        "contexto_rota_inicial": sessao.contexto_rota_inicial,
        "criado_em": sessao.criado_em.isoformat(),
        "atualizado_em": sessao.atualizado_em.isoformat(),
        "ia_processando": ia_proc,
        "mensagens": mensagens,
    }