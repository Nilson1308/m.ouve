"""Síntese LLM, budget cap, cache Redis e fallback determinístico."""

from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import date, datetime, timedelta
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.db.models import Sum
from django.utils import timezone

from atendimentos.models import (
    BriefingOperacionalIA,
    ConfiguracaoAgenteGestao,
    MensagemCopilotoGestor,
    Protocolo,
)
from atendimentos.services.agente_acoes import montar_acao_sugerida
from atendimentos.services.agente_fallback_narrativa import (
    insight_fallback_de_sinal,
    resumo_executivo_fallback,
)
from atendimentos.services.agente_sinais_service import coletar_fatos_operacionais
from catalogo.models import UnidadeAdministrativa

logger = logging.getLogger(__name__)

BRIEFING_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "resumo_executivo": {"type": "string"},
        "resumo_executivo_email": {"type": "string"},
        "insights": {
            "type": "array",
            "minItems": 1,
            "maxItems": 5,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "categoria": {
                        "type": "string",
                        "enum": ["acao_imediata", "tendencia_anomalia", "sugestao_conducao"],
                    },
                    "severidade": {
                        "type": "string",
                        "enum": ["critica", "alta", "media", "info"],
                    },
                    "titulo": {"type": "string"},
                    "evidencia_numerica": {"type": "string"},
                    "recomendacao": {"type": "string"},
                },
                "required": [
                    "id",
                    "categoria",
                    "severidade",
                    "titulo",
                    "evidencia_numerica",
                    "recomendacao",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": ["resumo_executivo", "resumo_executivo_email", "insights"],
    "additionalProperties": False,
}

SEVERIDADE_ORDEM = {"critica": 0, "alta": 1, "media": 2, "info": 3}
FORCAR_COOLDOWN_SEG = 15 * 60
ULTIMO_FALLBACK_CACHE_KEY = "agente_ia:ultimo_fallback_motivo"


def registrar_fallback_motivo(codigo: str, detalhe: str = "") -> None:
    payload = {
        "codigo": codigo,
        "detalhe": (detalhe or "")[:500],
        "em": timezone.now().isoformat(),
    }
    cache.set(ULTIMO_FALLBACK_CACHE_KEY, payload, timeout=86400 * 14)
    logger.info("Briefing IA fallback: %s %s", codigo, detalhe[:200] if detalhe else "")


def obter_ultimo_fallback_motivo() -> dict | None:
    raw = cache.get(ULTIMO_FALLBACK_CACHE_KEY)
    return raw if isinstance(raw, dict) else None


_GLOSSARIO_DOMINIO = """
Glossário (obrigatório):
- Inelegibilidade: cidadão barrado no chat por regra do catálogo. Nunca sugira treinar operadores;
  sugira revisar a regra/mensagem de orientação ao cidadão ou comunicação pública.
- Triagem parada / Crítico sem OS: recomende despacho imediato citando códigos PROT-..., serviço e secretaria.
- Concordância: use "1 protocolo" (singular), nunca "1 protocolos". Plural correto: "2 protocolos críticos".
- Evite conselhos vagos ("mapear no GIS") sem citar serviço, equipamento ou bairro presente no snapshot.
"""


def _sanitizar_gramatica_pt(texto: str) -> str:
    t = (texto or "").strip()
    if not t:
        return t
    t = re.sub(r"\b1\s+protocolos\b", "1 protocolo", t, flags=re.IGNORECASE)
    t = re.sub(r"\b1\s+críticos\b", "1 crítico", t, flags=re.IGNORECASE)
    t = re.sub(r"\b1\s+criticos\b", "1 crítico", t, flags=re.IGNORECASE)
    return t


def classificar_erro_llm(exc: BaseException) -> str:
    msg = str(exc).lower()
    if "json" in msg or "validate" in msg or "schema" in msg:
        return "json_invalido"
    if "429" in msg or "rate" in msg or "limite" in msg:
        return "erro_http"
    if "timeout" in msg or "timed out" in msg:
        return "timeout"
    return "erro_llm"


def invalidar_cache_briefing_protocolo(protocolo) -> None:
    """Invalida briefings do dia para escopos afetados pelo protocolo."""
    invalidar_cache_briefing_escopo("controladoria")
    invalidar_cache_briefing_escopo("ouvidoria")
    uid = None
    if getattr(protocolo, "servico_id", None) and protocolo.servico.unidade_responsavel_id:
        uid = protocolo.servico.unidade_responsavel_id
        invalidar_cache_briefing_escopo("unidade", uid)


def _cache_key_briefing(escopo_tipo: str, unidade_id, ref: date) -> str:
    uid = str(unidade_id) if unidade_id else "mun"
    return f"briefing_ia:{escopo_tipo}:{uid}:{ref.isoformat()}"


def _cache_key_forcar(escopo_tipo: str, unidade_id) -> str:
    uid = str(unidade_id) if unidade_id else "mun"
    return f"briefing_ia:forcar:{escopo_tipo}:{uid}"


def invalidar_cache_briefing_escopo(escopo_tipo: str, unidade_id=None) -> None:
    ref = timezone.localdate()
    cache.delete(_cache_key_briefing(escopo_tipo, unidade_id, ref))
    if unidade_id:
        cache.delete(_cache_key_briefing("unidade", unidade_id, ref))
    cache.delete(_cache_key_briefing("controladoria", None, ref))
    cache.delete(_cache_key_briefing("ouvidoria", None, ref))


def invalidar_cache_ao_protocolo_critico(protocolo) -> None:
    invalidar_cache_briefing_protocolo(protocolo)


def obter_consumo_tokens_mes(agora: datetime | None = None) -> int:
    agora = agora or timezone.now()
    ini = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    agg_b = BriefingOperacionalIA.objects.filter(criado_em__gte=ini).aggregate(
        ent=Sum("tokens_entrada"),
        sai=Sum("tokens_saida"),
    )
    agg_c = MensagemCopilotoGestor.objects.filter(
        criado_em__gte=ini,
        papel=MensagemCopilotoGestor.Papel.ASSISTENTE,
    ).aggregate(ent=Sum("tokens_entrada"), sai=Sum("tokens_saida"))
    return (
        int(agg_b["ent"] or 0)
        + int(agg_b["sai"] or 0)
        + int(agg_c["ent"] or 0)
        + int(agg_c["sai"] or 0)
    )


def _persona_instrucao(escopo_tipo: str) -> str:
    mapa = {
        "controladoria": (
            "Persona: Controlador-Geral. Foque transversal, SLA, risco financeiro e "
            "governança entre secretarias. Tom executivo e neutro."
        ),
        "ouvidoria": (
            "Persona: Ouvidor Municipal. Foque direitos do cidadão, cobrança respeitosa, "
            "urgências e retrabalho. Tom institucional."
        ),
        "unidade": (
            "Persona: Gestor setorial. Foque fila operacional, diligências, OS em campo "
            "e metas da unidade. Tom direto."
        ),
    }
    return mapa.get(escopo_tipo, mapa["controladoria"])


def _fallback_conteudo(fatos: dict, escopo_tipo: str) -> dict:
    sinais = list(fatos.get("sinais") or [])
    sinais.sort(key=lambda s: SEVERIDADE_ORDEM.get(s.get("severidade", "info"), 9))
    insights = [insight_fallback_de_sinal(s, escopo_tipo) for s in sinais[:5]]
    if not insights:
        insights = [
            insight_fallback_de_sinal(
                {
                    "id": "sem-sinais",
                    "detector": "sem-sinais",
                    "categoria": "sugestao_conducao",
                    "severidade": "info",
                    "titulo": "Operação estável no período",
                    "metricas": {},
                },
                escopo_tipo,
            )
        ]
        insights[0]["evidencia_numerica"] = "Nenhum alerta acima dos limiares"
        insights[0]["recomendacao"] = "Mantenha o acompanhamento rotineiro na Mesa de Trabalho."
    resumo, email = resumo_executivo_fallback(sinais, escopo_tipo)
    return {
        "resumo_executivo": resumo,
        "resumo_executivo_email": email,
        "insights": insights,
    }


def _validar_conteudo_ia(raw: dict, fatos: dict) -> dict:
    escopo = fatos.get("escopo_tipo", "controladoria")
    sinais = list(fatos.get("sinais") or [])
    sinais_por_id = {
        (s.get("id") or s.get("detector")): s for s in sinais if s.get("id") or s.get("detector")
    }
    out = dict(raw)
    insights_limpos = []
    for item in raw.get("insights") or []:
        if not isinstance(item, dict):
            continue
        insight_id = (item.get("id") or "").strip()
        base = sinais_por_id.get(insight_id)
        if base is None and not insight_id:
            titulo = (item.get("titulo") or "").strip()
            base = next((s for s in sinais if s.get("titulo") == titulo), None)
        if base:
            acao = base.get("acao_sugerida") or montar_acao_sugerida(
                base.get("detector") or insight_id,
                escopo_tipo=escopo,
                metricas=base.get("metricas"),
            )
            titulo = (item.get("titulo") or base.get("titulo") or "Insight").strip()
        else:
            titulo = (item.get("titulo") or "Insight").strip()
            acao = montar_acao_sugerida("sinal_generico", escopo_tipo=escopo, metricas={})
            acao["label"] = "Abrir Mesa de Trabalho"
        insights_limpos.append(
            {
                "id": (insight_id or (base.get("id") if base else str(uuid.uuid4())))[:64],
                "categoria": item.get("categoria") or (base or {}).get("categoria") or "tendencia_anomalia",
                "severidade": item.get("severidade") or (base or {}).get("severidade") or "media",
                "titulo": titulo,
                "evidencia_numerica": (item.get("evidencia_numerica") or "")[:300],
                "recomendacao": (item.get("recomendacao") or "")[:500],
                "acao_sugerida": acao,
            }
        )
    if not insights_limpos:
        raise ValueError("json_invalido")
    out["insights"] = insights_limpos[:5]
    out["resumo_executivo"] = _sanitizar_gramatica_pt(
        (out.get("resumo_executivo") or "").strip()[:1200]
    )
    out["resumo_executivo_email"] = _sanitizar_gramatica_pt(
        (out.get("resumo_executivo_email") or "").strip()[:800]
    )
    for item in out.get("insights") or []:
        if isinstance(item, dict):
            item["evidencia_numerica"] = _sanitizar_gramatica_pt(
                (item.get("evidencia_numerica") or "")[:300]
            )
            item["recomendacao"] = _sanitizar_gramatica_pt((item.get("recomendacao") or "")[:500])
    return out


def _chamar_llm_briefing(fatos: dict, escopo_tipo: str) -> tuple[dict, int, int, str]:
    from atendimentos.llm_orchestrator import _chamar_json_estruturado, _modelo

    sistema = (
        "Você é redator executivo do gabinete municipal. Sintetize o JSON de fatos em português "
        "claro, objetivo e acionável. Cite códigos PROT-…, serviços e prazos que constam no snapshot. "
        "NÃO invente números nem nomes/CPF/telefone/e-mail de cidadãos. "
        "Cada insight deve referenciar o campo id do sinal correspondente. "
        "evidencia_numerica: frase curta legível (sem nomes técnicos de campo). "
        "recomendacao: conduta concreta, sem repetir o título. "
        "resumo_executivo: parágrafo executivo completo (2–4 frases) visível no topo do painel. "
        f"{_GLOSSARIO_DOMINIO} "
        f"{_persona_instrucao(escopo_tipo)}"
    )
    mensagens = [
        {"role": "system", "content": sistema},
        {"role": "user", "content": json.dumps(fatos, ensure_ascii=False)},
    ]
    uso: list = []
    parsed = _chamar_json_estruturado(
        nome_schema="briefing_operacional",
        schema=BRIEFING_JSON_SCHEMA,
        mensagens=mensagens,
        strict=False,
        usage_sink=uso,
    )
    modelo = _modelo()
    if len(uso) >= 2:
        tokens_in, tokens_out = int(uso[0]), int(uso[1])
    else:
        tokens_in = max(500, len(json.dumps(fatos, ensure_ascii=False)) // 4)
        tokens_out = max(200, len(json.dumps(parsed, ensure_ascii=False)) // 4)
        logger.warning("Briefing LLM sem usage_sink; estimativa len/4 aplicada")
    return _validar_conteudo_ia(parsed, fatos), tokens_in, tokens_out, modelo


def _unidades_com_atividade() -> list[UnidadeAdministrativa]:
    limite = timezone.now() - timedelta(days=30)
    ids = (
        Protocolo.objects.filter(data_atualizacao__gte=limite)
        .exclude(status=Protocolo.Status.REJEITADO)
        .values_list("servico__unidade_responsavel_id", flat=True)
        .distinct()
    )
    return list(
        UnidadeAdministrativa.objects.filter(pk__in=[i for i in ids if i], ativo=True).order_by(
            "nome"
        )
    )


def _get_or_create_briefing_db(
    escopo_tipo: str,
    unidade_id,
    ref: date,
) -> BriefingOperacionalIA | None:
    return BriefingOperacionalIA.objects.filter(
        escopo_tipo=escopo_tipo,
        unidade_id=unidade_id,
        data_referencia=ref,
    ).first()


def verificar_rate_limit_forcar(escopo_tipo: str, unidade_id) -> tuple[bool, int | None]:
    chave = _cache_key_forcar(escopo_tipo, unidade_id)
    ttl = cache.ttl(chave) if hasattr(cache, "ttl") else None
    if cache.get(chave):
        return False, int(ttl) if ttl and ttl > 0 else FORCAR_COOLDOWN_SEG
    return True, None


def marcar_forcar_usado(escopo_tipo: str, unidade_id) -> None:
    cache.set(_cache_key_forcar(escopo_tipo, unidade_id), "1", timeout=FORCAR_COOLDOWN_SEG)


def gerar_briefing_escopo(
    escopo_tipo: str,
    *,
    unidade: UnidadeAdministrativa | None = None,
    forcar: bool = False,
) -> BriefingOperacionalIA:
    cfg = ConfiguracaoAgenteGestao.load()
    ref = timezone.localdate()
    unidade_id = unidade.pk if unidade else None

    if not forcar:
        cached = cache.get(_cache_key_briefing(escopo_tipo, unidade_id, ref))
        if isinstance(cached, str):
            existente = BriefingOperacionalIA.objects.filter(pk=cached).first()
            if existente:
                return existente
        existente = _get_or_create_briefing_db(escopo_tipo, unidade_id, ref)
        if existente:
            cache.set(
                _cache_key_briefing(escopo_tipo, unidade_id, ref),
                str(existente.pk),
                timeout=86400,
            )
            return existente

    fatos = coletar_fatos_operacionais(escopo_tipo, unidade=unidade, config=cfg)
    consumo = obter_consumo_tokens_mes()
    api_key = (getattr(settings, "LLM_CHAT_API_KEY", "") or "").strip()
    usar_llm = (
        cfg.agente_ativo
        and bool(api_key)
        and consumo < int(cfg.orcamento_tokens_mensal)
    )

    modo = BriefingOperacionalIA.ModoGeracao.FALLBACK
    modelo = ""
    tokens_in = 0
    tokens_out = 0
    conteudo = _fallback_conteudo(fatos, escopo_tipo)

    if not cfg.agente_ativo:
        registrar_fallback_motivo("agente_inativo")
    elif not api_key:
        registrar_fallback_motivo("sem_api_key")
    elif consumo >= int(cfg.orcamento_tokens_mensal):
        registrar_fallback_motivo("budget_esgotado", f"consumo={consumo}")

    if usar_llm:
        try:
            conteudo, tokens_in, tokens_out, modelo = _chamar_llm_briefing(fatos, escopo_tipo)
            modo = BriefingOperacionalIA.ModoGeracao.LLM
        except Exception as exc:
            codigo = classificar_erro_llm(exc)
            registrar_fallback_motivo(codigo, str(exc))
            logger.warning("Briefing LLM falhou (%s): %s", escopo_tipo, exc)
    elif cfg.agente_ativo and api_key and consumo >= int(cfg.orcamento_tokens_mensal):
        pass
    elif not api_key or not cfg.agente_ativo:
        pass

    briefing, _created = BriefingOperacionalIA.objects.update_or_create(
        escopo_tipo=escopo_tipo,
        unidade=unidade,
        data_referencia=ref,
        defaults={
            "fatos_deterministicos": fatos,
            "conteudo_ia": conteudo,
            "resumo_executivo_email": conteudo.get("resumo_executivo_email") or "",
            "modo_geracao": modo,
            "modelo_llm": modelo,
            "tokens_entrada": tokens_in,
            "tokens_saida": tokens_out,
        },
    )
    cache.set(
        _cache_key_briefing(escopo_tipo, unidade_id, ref),
        str(briefing.pk),
        timeout=86400,
    )
    return briefing


def obter_briefing_digest_unidade(unidade: UnidadeAdministrativa) -> dict | None:
    cfg = ConfiguracaoAgenteGestao.load()
    if not cfg.incluir_resumo_no_digest_email or not cfg.agente_ativo:
        return None
    try:
        b = gerar_briefing_escopo("unidade", unidade=unidade, forcar=False)
        return _bloco_digest(b)
    except Exception as exc:
        logger.warning("Briefing digest unidade falhou: %s", exc)
        return None


def obter_briefing_digest_controladoria() -> dict | None:
    cfg = ConfiguracaoAgenteGestao.load()
    if not cfg.incluir_resumo_no_digest_email or not cfg.agente_ativo:
        return None
    try:
        b = gerar_briefing_escopo("controladoria", forcar=False)
        return _bloco_digest(b, titulo="Radar IA — Síntese Executiva do Município")
    except Exception as exc:
        logger.warning("Briefing digest controladoria falhou: %s", exc)
        return None


def _bloco_digest(briefing: BriefingOperacionalIA, titulo: str | None = None) -> dict:
    conteudo = briefing.conteudo_ia or {}
    insights = list(conteudo.get("insights") or [])[:3]
    return {
        "titulo": titulo or "Radar IA — Síntese da Pasta",
        "resumo": briefing.resumo_executivo_email
        or conteudo.get("resumo_executivo_email")
        or "",
        "alertas_top3": [
            {"titulo": i.get("titulo"), "severidade": i.get("severidade")} for i in insights
        ],
    }


def gerar_briefings_operacionais_diarios() -> int:
    cfg = ConfiguracaoAgenteGestao.load()
    agora = timezone.localtime()
    if not cfg.agente_ativo or not cfg.briefing_proativo_ativo:
        return 0
    if agora.hour != int(cfg.briefing_hora_geracao):
        return 0
    cache_key = f"briefing_diario_job:{agora.date().isoformat()}"
    if cache.get(cache_key):
        return 0
    cache.set(cache_key, "1", timeout=86400)
    total = 0
    total += 1
    gerar_briefing_escopo("controladoria", forcar=False)
    total += 1
    gerar_briefing_escopo("ouvidoria", forcar=False)
    for unidade in _unidades_com_atividade():
        gerar_briefing_escopo("unidade", unidade=unidade, forcar=False)
        total += 1
    return total