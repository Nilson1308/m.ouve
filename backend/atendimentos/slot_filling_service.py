"""Slot filling na abertura: extrai campos do schema a partir da 1ª mensagem substantiva."""

from __future__ import annotations

import hashlib
import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Any

from django.conf import settings
from django.core.cache import cache

from atendimentos.chat_estado import set_meta
from atendimentos.chat_resumo import _formatar_valor
from atendimentos.models import MensagemChat, SessaoChat
from catalogo.models import ServicoCatalogo

logger = logging.getLogger(__name__)

CONFIDENCA_MINIMA = 0.80
CACHE_TTL_SEG = 3600
LLM_TIMEOUT_SEG = 12
TAMANHO_MINIMO_ABERTURA = 20

_SAUDACOES_CURTAS = frozenset(
    {
        "oi",
        "olá",
        "ola",
        "bom dia",
        "boa tarde",
        "boa noite",
        "hey",
        "e aí",
        "e ai",
    }
)

_CONFIRMACOES_CURTAS = frozenset({"sim", "s", "não", "nao", "n", "ok", "confirmo"})

_INTENCAO_SEM_DETALHE = re.compile(
    r"^(quero\s+(fazer|dar|registrar|manifestar|reclamar|solicitar)|gostaria de)\b",
    re.I,
)


def _schema_props(servico: ServicoCatalogo) -> dict[str, dict]:
    schema = dict(servico.schema_formulario or {})
    schema.pop("$metadata", None)
    schema.pop("$schema", None)
    return dict(schema.get("properties") or {})


def texto_elegivel_abertura(texto: str) -> bool:
    t = (texto or "").strip()
    if len(t) < TAMANHO_MINIMO_ABERTURA:
        return False
    tl = t.lower()
    if tl in _CONFIRMACOES_CURTAS:
        return False
    if tl in _SAUDACOES_CURTAS:
        return False
    if tl.startswith("📍") or tl.startswith("✓"):
        return False
    return True


def obter_mensagem_abertura_substantiva(sessao: SessaoChat) -> str | None:
    """Primeira mensagem do cidadão com conteúdo suficiente para slot filling."""
    qs = (
        MensagemChat.objects.filter(
            sessao=sessao,
            autor=MensagemChat.Autor.CIDADAO,
        )
        .order_by("criado_em")
    )
    for msg in qs:
        bruto = (msg.conteudo_texto or "").strip()
        if bruto == "(sem texto)":
            continue
        if texto_elegivel_abertura(bruto):
            return bruto
    return None


def _hash_mensagem(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


def _cache_key(sessao_id, texto_hash: str) -> str:
    return f"slot_filling:{sessao_id}:{texto_hash}"


def _campo_ignorado_slot_filling(prop: dict) -> bool:
    if not isinstance(prop, dict):
        return True
    fmt = (prop.get("format") or "").lower()
    if fmt in ("uri", "data-url", "binary"):
        return True
    if prop.get("x-ouvia-tipo-campo") in ("image", "geolocation", "lookup"):
        return True
    if prop.get("x-ouvia-datasource"):
        return True
    if prop.get("type") == "array":
        items = prop.get("items") or {}
        if items.get("x-ouvia-datasource"):
            return True
    return False


def campos_elegiveis_para_prompt(servico: ServicoCatalogo) -> list[dict[str, Any]]:
    props = _schema_props(servico)
    ordem = (servico.schema_formulario or {}).get("$metadata", {}).get("ordem_campos") or []
    if not ordem:
        ordem = list(props.keys())
    out: list[dict[str, Any]] = []
    for chave in ordem:
        if chave not in props:
            continue
        prop = props[chave]
        if _campo_ignorado_slot_filling(prop):
            continue
        item: dict[str, Any] = {
            "chave": chave,
            "title": prop.get("title") or prop.get("x-ouvia-ui-pergunta") or chave,
            "type": prop.get("type") or "string",
        }
        if prop.get("enum"):
            item["enum"] = prop["enum"]
            item["enumNames"] = prop.get("enumNames") or prop["enum"]
        if prop.get("type") == "array":
            items = prop.get("items") or {}
            if items.get("enum"):
                item["type"] = "array"
                item["enum"] = items["enum"]
                item["enumNames"] = items.get("enumNames") or items["enum"]
        if prop.get("minimum") is not None:
            item["minimum"] = prop["minimum"]
        if prop.get("maximum") is not None:
            item["maximum"] = prop["maximum"]
        if prop.get("minLength") is not None:
            item["minLength"] = prop["minLength"]
        out.append(item)
    return out


def _mapear_enum(prop: dict, bruto: Any) -> Any | None:
    enums = prop.get("enum") or []
    if prop.get("type") == "array":
        enums = (prop.get("items") or {}).get("enum") or []
    if not enums:
        return bruto
    if bruto in enums:
        return bruto
    texto = str(bruto or "").strip()
    if not texto:
        return None
    labels = prop.get("enumNames") or enums
    if prop.get("type") == "array":
        labels = (prop.get("items") or {}).get("enumNames") or labels
    texto_l = texto.lower()
    for val, label in zip(enums, labels, strict=False):
        if str(val).lower() == texto_l:
            return val
        if str(label).strip().lower() == texto_l:
            return val
    return None


def _validar_valor_campo(prop: dict, valor: Any, confianca: float) -> Any | None:
    if confianca < CONFIDENCA_MINIMA:
        return None
    tipo = prop.get("type") or "string"

    if tipo == "boolean":
        if isinstance(valor, bool):
            return valor
        if isinstance(valor, str):
            vl = valor.strip().lower()
            if vl in ("sim", "s", "true", "1"):
                return True
            if vl in ("não", "nao", "n", "false", "0"):
                return False
        return None

    if tipo in ("number", "integer"):
        try:
            n = float(valor) if tipo == "number" else int(float(valor))
        except (TypeError, ValueError):
            return None
        if prop.get("minimum") is not None and n < prop["minimum"]:
            return None
        if prop.get("maximum") is not None and n > prop["maximum"]:
            return None
        return int(n) if tipo == "integer" else n

    if prop.get("enum") or (tipo == "array" and (prop.get("items") or {}).get("enum")):
        mapeado = _mapear_enum(prop, valor)
        return mapeado

    if tipo == "string" or tipo == "array":
        s = str(valor or "").strip()
        if not s:
            return None
        min_len = int(prop.get("minLength") or 0)
        if min_len > 0 and len(s) < min_len:
            return None
        if min_len == 0 and len(s) < 8:
            return None
        if _INTENCAO_SEM_DETALHE.match(s) and len(s) < 55:
            return None
        return s

    return None


def validar_campos_extraidos(
    servico: ServicoCatalogo,
    raw_campos: dict,
    dados_existentes: dict,
) -> dict[str, Any]:
    props = _schema_props(servico)
    aceitos: dict[str, Any] = {}
    if not isinstance(raw_campos, dict):
        return aceitos
    for chave, payload in raw_campos.items():
        if chave in dados_existentes and dados_existentes.get(chave) not in (None, "", []):
            continue
        if chave not in props:
            continue
        if not isinstance(payload, dict):
            continue
        try:
            conf = float(payload.get("confianca") or 0)
        except (TypeError, ValueError):
            conf = 0.0
        valor_ok = _validar_valor_campo(props[chave], payload.get("valor"), conf)
        if valor_ok is not None:
            aceitos[chave] = valor_ok
    return aceitos


def _mesclar_dados_sem_sobrescrever(sessao: SessaoChat, novos: dict[str, Any]) -> dict[str, Any]:
    if not novos:
        return {}
    dados = dict(sessao.dados_coletados or {})
    aplicados: dict[str, Any] = {}
    for chave, valor in novos.items():
        if str(chave).startswith("_"):
            continue
        atual = dados.get(chave)
        if atual not in (None, "", []) and str(atual).strip():
            continue
        dados[chave] = valor
        aplicados[chave] = valor
    if aplicados:
        sessao.dados_coletados = dados
        sessao.save(update_fields=["dados_coletados", "atualizado_em"])
    return aplicados


def _rotulos_campos_preenchidos(servico: ServicoCatalogo, campos: dict[str, Any]) -> list[str]:
    props = _schema_props(servico)
    partes: list[str] = []
    for chave, valor in campos.items():
        prop = props.get(chave) or {}
        titulo = (prop.get("title") or prop.get("x-ouvia-ui-pergunta") or chave).strip()
        rotulo_valor = _formatar_valor(prop, valor)
        partes.append(f"{titulo}: {rotulo_valor}")
    return partes


def montar_prefixo_confirmacao(servico: ServicoCatalogo, campos: dict[str, Any]) -> str:
    partes = _rotulos_campos_preenchidos(servico, campos)
    if not partes:
        return ""
    if len(partes) == 1:
        return f"Entendi! Já identifiquei {partes[0]} pelo seu relato."
    corpo = ", ".join(partes[:-1]) + f" e {partes[-1]}"
    return f"Entendi! Já identifiquei {corpo} pelo seu relato."


SLOT_FILLING_LLM_SCHEMA = {
    "type": "object",
    "properties": {
        "campos": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "valor": {},
                    "confianca": {"type": "number"},
                },
                "required": ["valor", "confianca"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["campos"],
    "additionalProperties": False,
}


def _llm_disponivel() -> bool:
    return bool((getattr(settings, "LLM_CHAT_API_KEY", "") or "").strip())


def _chamar_llm_slot_filling(texto: str, servico: ServicoCatalogo) -> dict | None:
    from atendimentos.llm_orchestrator import (
        ChatOrchestrationError,
        _chamar_json_estruturado,
        _prepend_tom_llm,
    )

    elegiveis = campos_elegiveis_para_prompt(servico)
    if not elegiveis:
        return None

    mensagens = _prepend_tom_llm(
        [
            {
                "role": "system",
                "content": (
                    "Extraia da mensagem do cidadão apenas campos explicitamente presentes. "
                    "Retorne JSON {campos: {chave: {valor, confianca}}}. "
                    f"Preencha só com confianca>= {CONFIDENCA_MINIMA} mental; caso contrário omita o campo. "
                    "Para enums use o valor técnico da lista enum, não invente. "
                    "Não preencha descrições que sejam só intenção vaga sem o fato concreto."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "mensagem_cidadao": texto,
                        "campos_formulario": elegiveis,
                    },
                    ensure_ascii=False,
                ),
            },
        ],
        servico,
    )

    def _call():
        return _chamar_json_estruturado(
            nome_schema="slot_filling_abertura",
            schema=SLOT_FILLING_LLM_SCHEMA,
            mensagens=mensagens,
            strict=False,
        )

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(_call)
        try:
            return future.result(timeout=LLM_TIMEOUT_SEG)
        except FuturesTimeoutError:
            logger.warning("Slot filling: timeout LLM (%ss)", LLM_TIMEOUT_SEG)
            return None
        except ChatOrchestrationError as exc:
            logger.warning("Slot filling: LLM indisponível: %s", exc)
            return None
        except Exception:
            logger.exception("Slot filling: falha na extração")
            return None


def aplicar_slot_filling_abertura(
    sessao: SessaoChat,
    servico: ServicoCatalogo,
) -> tuple[str, dict[str, Any]]:
    """
    Tenta preencher campos a partir da mensagem de abertura.

    Retorna (prefixo_ux, campos_aplicados). Silencioso em falhas.
    """
    texto = obter_mensagem_abertura_substantiva(sessao)
    if not texto:
        return "", {}

    if not _llm_disponivel():
        return "", {}

    h = _hash_mensagem(texto)
    ck = _cache_key(sessao.pk, h)

    dados_existentes = {
        k: v
        for k, v in (sessao.dados_coletados or {}).items()
        if not str(k).startswith("_")
    }

    cached = cache.get(ck)
    if isinstance(cached, dict) and "campos_validados" in cached:
        campos_validados = dict(cached.get("campos_validados") or {})
    else:
        llm_out = _chamar_llm_slot_filling(texto, servico)
        if not llm_out:
            cache.set(ck, {"campos_validados": {}, "campos_raw": {}}, CACHE_TTL_SEG)
            return "", {}
        raw_campos = llm_out.get("campos") if isinstance(llm_out.get("campos"), dict) else {}
        campos_validados = validar_campos_extraidos(servico, raw_campos, dados_existentes)
        cache.set(
            ck,
            {"campos_validados": campos_validados, "campos_raw": raw_campos},
            CACHE_TTL_SEG,
        )

    aplicados = _mesclar_dados_sem_sobrescrever(sessao, campos_validados)
    if aplicados:
        set_meta(
            sessao,
            slot_filling_hash=h,
            slot_filling_campos=sorted(aplicados.keys()),
        )
        sessao.save(update_fields=["dados_coletados", "atualizado_em"])

    prefixo = montar_prefixo_confirmacao(servico, aplicados)
    return prefixo, aplicados