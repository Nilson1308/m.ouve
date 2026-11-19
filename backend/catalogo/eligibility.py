"""Avaliação de regras de elegibilidade configuradas no catálogo (chat PWA)."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def _normalizar_texto(valor: str) -> str:
    return re.sub(r"\s+", " ", (valor or "").strip().lower())


def idade_em_meses(valor: Any, *, campo_numerico: bool = False) -> int | None:
    """Converte resposta de idade para meses (melhor esforço, pt-BR)."""
    if valor is None:
        return None
    if isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        n = int(valor)
        if campo_numerico:
            return n * 12
        return n * 12 if n <= 25 else n
    texto = _normalizar_texto(str(valor))
    if not texto:
        return None
    if any(p in texto for p in ("filhote", "recém", "recem", "lactante")):
        return 2
    anos = re.search(r"(\d+)\s*(?:anos?|a\.?)(?:\s|$)", texto)
    if anos:
        return int(anos.group(1)) * 12
    meses = re.search(r"(\d+)\s*(?:meses?|m\.?)(?:\s|$)", texto)
    if meses:
        return int(meses.group(1))
    so_num = re.match(r"^(\d+)$", texto)
    if so_num:
        n = int(so_num.group(1))
        return n * 12 if (campo_numerico or n <= 25) else n
    return None


def avaliar_regra_texto(regra: dict, valor: Any) -> bool:
    alvos = regra.get("valores") or []
    if not isinstance(alvos, list) or not alvos:
        return False
    valor_norm = _normalizar_texto(str(valor))
    alvos_norm = {_normalizar_texto(str(a)) for a in alvos if str(a).strip()}
    if valor_norm in alvos_norm:
        return True
    return any(a in valor_norm for a in alvos_norm)


def avaliar_regra_idade_faixa(
    regra: dict, valor: Any, *, campo_numerico: bool = False
) -> bool:
    """Retorna True se deve BLOQUEAR (fora da faixa)."""
    meses = idade_em_meses(valor, campo_numerico=campo_numerico)
    if meses is None:
        return False
    try:
        min_m = int(regra.get("idade_min_meses") or 0)
    except (TypeError, ValueError):
        min_m = 0
    try:
        max_a = int(regra.get("idade_max_anos") or 0)
    except (TypeError, ValueError):
        max_a = 0
    max_meses = max_a * 12 if max_a > 0 else None

    if min_m > 0 and meses < min_m:
        return True
    if max_meses is not None and meses > max_meses:
        return True
    return False


def _tem_valor_campo(dados: dict, chave: str) -> bool:
    valor = (dados or {}).get(chave)
    if valor is None:
        return False
    if isinstance(valor, str):
        return bool(valor.strip())
    return True


def _bloqueio_idade_por_condicao(
    condicao: str, valor: Any, *, campo_numerico: bool = False
) -> bool | None:
    """Decisão determinística para faixa de idade (sem LLM). None = não aplicável."""
    texto_cond = (condicao or "").lower()
    if not any(p in texto_cond for p in ("idade", "meses", "anos", "filhote")):
        return None
    meses = idade_em_meses(valor, campo_numerico=campo_numerico)
    if meses is None:
        return None
    min_m = 0
    max_meses: int | None = None
    m_min = re.search(r"menor que\s+(\d+)\s*meses", texto_cond)
    if m_min:
        min_m = int(m_min.group(1))
    m_max_a = re.search(r"maior que\s+(\d+)\s*anos", texto_cond)
    if m_max_a:
        max_meses = int(m_max_a.group(1)) * 12
    if min_m <= 0 and max_meses is None:
        return None
    if min_m > 0 and meses < min_m:
        return True
    if max_meses is not None and meses > max_meses:
        return True
    return False


def _bloqueio_doenca_por_condicao(condicao: str, valor: Any) -> bool | None:
    texto_cond = (condicao or "").lower()
    if not any(p in texto_cond for p in ("doen", "sintom", "saúde", "saude")):
        return None
    v = _normalizar_texto(str(valor))
    if v in ("sim", "s", "yes"):
        return True
    if any(p in v for p in ("doente", "doenca", "doença", "sintoma", "tratamento")):
        return True
    return False


def _bloqueio_protocolo_deterministico(condicao: str, dados: dict) -> bool | None:
    """Cruza idade/doença quando a condição menciona ambos (sem LLM)."""
    texto = (condicao or "").lower()
    citou_idade = "idade" in texto or "meses" in texto or "anos" in texto
    citou_doenca = "doen" in texto or "saúde" in texto or "saude" in texto or "sintom" in texto

    if citou_idade and citou_doenca:
        if not _tem_valor_campo(dados, "idade") or not _tem_valor_campo(dados, "doencas"):
            return False

    bloqueou = False
    if citou_idade and _tem_valor_campo(dados, "idade"):
        r = _bloqueio_idade_por_condicao(condicao, dados.get("idade"))
        if r is True:
            bloqueou = True
    if citou_doenca and _tem_valor_campo(dados, "doencas"):
        r = _bloqueio_doenca_por_condicao(condicao, dados.get("doencas"))
        if r is True:
            bloqueou = True
    if bloqueou:
        return True
    if citou_idade or citou_doenca:
        return False
    return None


def avaliar_regra_interpretacao(
    condicao: str,
    valor: Any,
    *,
    nome_campo: str,
    pergunta_campo: str = "",
    nome_servico: str = "",
    servico=None,
) -> bool:
    """
    Regra genérica: a prefeitura descreve a condição em português;
    a IA decide se a resposta do cidadão ativa o bloqueio.
    """
    condicao = (condicao or "").strip()
    if not condicao:
        return False
    if valor is None or (isinstance(valor, str) and not str(valor).strip()):
        return False

    campo_num = nome_campo.endswith("_anos") or nome_campo == "idade_anos"
    det = _bloqueio_idade_por_condicao(condicao, valor, campo_numerico=campo_num)
    if det is not None:
        return det
    det = _bloqueio_doenca_por_condicao(condicao, valor)
    if det is not None:
        return det

    try:
        from atendimentos.llm_orchestrator import (
            ChatOrchestrationError,
            _chamar_json_estruturado,
            _prepend_tom_llm,
        )
    except ImportError:
        return False

    schema = {
        "type": "object",
        "properties": {"deve_bloquear": {"type": "boolean"}},
        "required": ["deve_bloquear"],
        "additionalProperties": False,
    }
    payload = {
        "condicao_bloqueio": condicao,
        "pergunta_do_assistente": pergunta_campo,
        "campo_protocolo": nome_campo,
        "resposta_cidadao": valor,
        "nome_servico": nome_servico,
    }
    mensagens = _prepend_tom_llm(
        [
            {
                "role": "system",
                "content": (
                    "Você aplica regras de elegibilidade municipal (M.Ouve). "
                    "Dada a CONDIÇÃO escrita pelo gestor e a RESPOSTA do cidadão, "
                    "retorne deve_bloquear=true somente quando a condição estiver "
                    "claramente satisfeita. Em dúvida, deve_bloquear=false."
                ),
            },
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        servico,
    )
    try:
        parsed = _chamar_json_estruturado(
            nome_schema="elegibilidade",
            schema=schema,
            mensagens=mensagens,
            strict=True,
        )
        return bool(parsed.get("deve_bloquear"))
    except ChatOrchestrationError:
        logger.warning("LLM indisponível para regra de elegibilidade em %s", nome_campo)
        return False
    except Exception:
        logger.exception("Falha ao avaliar regra interpretativa")
        return False


def _dados_protocolo_para_llm(dados: dict, props: dict[str, dict]) -> dict[str, Any]:
    """Monta visão legível do protocolo (só campos já preenchidos)."""
    snapshot: dict[str, Any] = {}
    for chave, valor in (dados or {}).items():
        if valor is None or (isinstance(valor, str) and not str(valor).strip()):
            continue
        prop = props.get(chave) or {}
        rotulo = (
            (prop.get("x-ouvia-ui-pergunta") or prop.get("description") or prop.get("title") or chave)
        ).strip()
        snapshot[chave] = {
            "rotulo": rotulo,
            "valor": valor,
        }
    return snapshot


def avaliar_regra_interpretacao_protocolo(
    condicao: str,
    dados: dict,
    props: dict[str, dict],
    *,
    nome_servico: str = "",
    servico=None,
) -> bool:
    """Regra genérica sobre vários campos do protocolo (condição em português + LLM)."""
    condicao = (condicao or "").strip()
    if not condicao:
        return False
    protocolo = _dados_protocolo_para_llm(dados, props)
    if not protocolo:
        return False

    det = _bloqueio_protocolo_deterministico(condicao, dados)
    if det is not None:
        return det

    try:
        from atendimentos.llm_orchestrator import (
            ChatOrchestrationError,
            _chamar_json_estruturado,
            _prepend_tom_llm,
        )
    except ImportError:
        return False

    schema = {
        "type": "object",
        "properties": {"deve_bloquear": {"type": "boolean"}},
        "required": ["deve_bloquear"],
        "additionalProperties": False,
    }
    payload = {
        "condicao_bloqueio": condicao,
        "dados_protocolo": protocolo,
        "nome_servico": nome_servico,
    }
    mensagens = _prepend_tom_llm(
        [
            {
                "role": "system",
                "content": (
                    "Você aplica regras de elegibilidade municipal (M.Ouve) sobre o "
                    "PROTOCOLO COMPLETO já coletado no chat. "
                    "Considere todos os campos em dados_protocolo. "
                    "Retorne deve_bloquear=true somente quando a condição do gestor "
                    "estiver claramente satisfeita. Se faltar informação para decidir, "
                    "deve_bloquear=false."
                ),
            },
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        servico,
    )
    try:
        parsed = _chamar_json_estruturado(
            nome_schema="elegibilidade_protocolo",
            schema=schema,
            mensagens=mensagens,
            strict=True,
        )
        return bool(parsed.get("deve_bloquear"))
    except ChatOrchestrationError:
        logger.warning("LLM indisponível para regra de protocolo em %s", nome_servico)
        return False
    except Exception:
        logger.exception("Falha ao avaliar regra interpretativa de protocolo")
        return False


def _escopo_protocolo(regra: dict) -> bool:
    escopo = (regra.get("escopo") or "").strip().lower()
    if escopo == "protocolo":
        return True
    tipo = (regra.get("tipo") or "").strip().lower()
    return tipo in ("interpretacao_protocolo", "protocolo")


def rotulo_motivo_inelegibilidade(regra: dict, prop: dict | None = None) -> str:
    """Identificador legível para dashboards (até 255 chars)."""
    campo = (regra.get("campo") or "").strip()
    tipo = (regra.get("tipo") or "interpretacao").strip().lower()
    if campo:
        titulo = ""
        if prop:
            titulo = (
                prop.get("x-ouvia-ui-pergunta")
                or prop.get("title")
                or prop.get("description")
                or ""
            ).strip()
        if not titulo:
            titulo = campo.replace("_", " ").title()
        return f"{titulo} · regra {tipo}"[:255]
    cond = (regra.get("condicao") or "Regra de protocolo").strip()
    return f"Protocolo · {cond[:220]}"[:255]


def avaliar_regras_campos_com_motivo(
    regras: list[dict],
    dados: dict,
    props: dict[str, dict],
    *,
    nome_servico: str = "",
    servico=None,
) -> tuple[str | None, str | None]:
    """Retorna (mensagem ao cidadão, rótulo da regra) quando alguma regra bloqueia."""
    if not isinstance(regras, list):
        return None, None
    for regra in regras:
        if not isinstance(regra, dict):
            continue
        if regra.get("ativo") is False:
            continue
        mensagem = (regra.get("mensagem") or "").strip()
        if not mensagem:
            continue

        if _escopo_protocolo(regra):
            condicao = (regra.get("condicao") or "").strip()
            bloquear = avaliar_regra_interpretacao_protocolo(
                condicao,
                dados,
                props,
                nome_servico=nome_servico,
                servico=servico,
            )
            if bloquear:
                return mensagem, rotulo_motivo_inelegibilidade(regra, None)
            continue

        campo = (regra.get("campo") or "").strip()
        if not campo or campo not in dados:
            continue
        valor = dados.get(campo)
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            continue
        tipo = (regra.get("tipo") or "texto").strip().lower()
        prop = props.get(campo) or {}
        campo_num = prop.get("type") == "number"
        bloquear = False
        if tipo in ("texto", "match", "texto_match"):
            bloquear = avaliar_regra_texto(regra, valor)
        elif tipo in ("idade_faixa", "idade"):
            bloquear = avaliar_regra_idade_faixa(regra, valor, campo_numerico=campo_num)
        elif tipo in ("interpretacao", "nl", "natural"):
            condicao = (regra.get("condicao") or "").strip()
            pergunta = (
                (prop.get("x-ouvia-ui-pergunta") or prop.get("description") or prop.get("title") or "")
            ).strip()
            bloquear = avaliar_regra_interpretacao(
                condicao,
                valor,
                nome_campo=campo,
                pergunta_campo=pergunta,
                nome_servico=nome_servico,
                servico=servico,
            )
        if bloquear:
            return mensagem, rotulo_motivo_inelegibilidade(regra, prop)
    return None, None


def avaliar_regras_campos(
    regras: list[dict],
    dados: dict,
    props: dict[str, dict],
    *,
    nome_servico: str = "",
    servico=None,
) -> str | None:
    mensagem, _motivo = avaliar_regras_campos_com_motivo(
        regras, dados, props, nome_servico=nome_servico, servico=servico
    )
    return mensagem