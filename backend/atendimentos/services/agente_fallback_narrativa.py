"""Texto executivo do fallback do Radar (sem chaves técnicas)."""

from __future__ import annotations

import re
from typing import Any

from atendimentos.services.agente_acoes import montar_acao_sugerida

_PROIBIDO = re.compile(r"(=|motivo_hash|fallback|media_semanal)", re.I)


def _truncate_words(texto: str, max_palavras: int = 12) -> str:
    palavras = (texto or "").split()
    if len(palavras) <= max_palavras:
        return texto.strip()
    return " ".join(palavras[:max_palavras]).strip() + "…"


def _inteiro(valor, default: int = 0) -> int:
    try:
        if valor is None:
            return default
        return int(valor)
    except (TypeError, ValueError):
        return default


def _plural(n: int, um: str, muitos: str) -> str:
    return um if n == 1 else muitos


def _lista_prot(codigos: list) -> str:
    c = [str(x) for x in (codigos or [])[:3] if x]
    if not c:
        return ""
    if len(c) == 1:
        return c[0]
    if len(c) == 2:
        return f"{c[0]} e {c[1]}"
    return f"{c[0]}, {c[1]} e mais {len(c) - 2}"


def _servicos_txt(metricas: dict) -> str:
    nomes = metricas.get("servicos_principais") or metricas.get("servico_nome")
    if isinstance(nomes, list) and nomes:
        return nomes[0] if len(nomes) == 1 else f"{nomes[0]} e outros"
    if isinstance(nomes, str) and nomes:
        return nomes
    return ""


def narrativa_evidencia(detector: str, metricas: dict) -> str:
    m = metricas or {}
    codigos = m.get("protocolos_exemplo") or m.get("codigos") or []
    n = _inteiro(m.get("total") or m.get("volume_7d") or m.get("total_em_analise_parado"), 0)

    if detector == "critico_sem_campo":
        n = _inteiro(m.get("total_criticos_sem_os"), n or len(codigos))
        return _plural(n, "1 protocolo crítico sem OS", f"{n} protocolos críticos sem OS")
    if detector == "triagem_parada":
        n = _inteiro(m.get("total_em_analise_parado"), n)
        dias = _inteiro(m.get("dias_parado_max"), 0)
        base = _plural(n, "1 protocolo parado na triagem", f"{n} protocolos na triagem")
        if dias:
            return f"{base} · mais antigo há {dias} dias"
        return base
    if detector == "diligencia_respondida_pendente":
        n = _inteiro(m.get("total_respondidas_pendentes"), len(codigos))
        return _plural(n, "1 diligência respondida aguardando ação", f"{n} diligências respondidas aguardando ação")
    if detector == "sla_vencido":
        n = _inteiro(m.get("total_vencidos"), n)
        return _plural(n, "1 protocolo com SLA vencido", f"{n} protocolos com SLA vencido")
    if detector == "pico_bairro":
        if m.get("novo_foco"):
            vol = _inteiro(m.get("volume_7d"), n)
            return f"{vol} registros em 7 dias · novo foco de demanda"
        vol = int(m.get("volume_7d") or n)
        pct = _inteiro(m.get("crescimento_percentual"), 0)
        return f"{vol} registros em 7 dias · alta de {pct}%"
    if detector == "pico_equipamento":
        if m.get("novo_foco"):
            vol = _inteiro(m.get("volume_7d"), n)
            return f"{vol} chamados no equipamento · novo foco"
        vol = int(m.get("volume_7d") or n)
        pct = _inteiro(m.get("crescimento_percentual"), 0)
        return f"{vol} chamados · alta de {pct}%"
    if detector == "inelegibilidade":
        n = _inteiro(m.get("ocorrencias_30d"), n)
        return _plural(n, "1 bloqueio nos últimos 30 dias", f"{n} bloqueios nos últimos 30 dias")
    if detector == "sugestao_urgencia_pendente":
        n = _inteiro(m.get("total_sugestoes_pendentes"), n)
        return _plural(n, "1 sugestão de urgência pendente", f"{n} sugestões de urgência pendentes")
    if m.get("total") is not None:
        return f"{_inteiro(m['total'])} registros"
    return "Situação monitorada"


def narrativa_recomendacao(detector: str, metricas: dict, escopo_tipo: str) -> str:
    m = metricas or {}
    codigos = list(m.get("protocolos_exemplo") or m.get("codigos") or [])[:3]
    prot = _lista_prot(codigos)
    srv = _servicos_txt(m)

    if detector == "critico_sem_campo" and prot:
        extra = f" ({srv})" if srv else ""
        return (
            f"Despache equipe de campo para {prot}{extra} ainda hoje, "
            "confirmando prazo de SLA na Mesa."
        )
    if detector == "triagem_parada" and prot:
        return (
            f"Retome a análise de {prot} na fila «em análise» e registre despacho "
            "ou devolutiva ao cidadão."
        )
    if detector == "diligencia_respondida_pendente" and prot:
        return (
            f"O cidadão já respondeu em {prot}. Valide anexos e providencie "
            "despacho ou OS antes que o caso volte a atrasar."
        )
    if detector == "sla_vencido":
        if prot:
            return f"Priorize {prot} no relatório de atrasos e alinhe retorno formal ao cidadão."
        return "Revise o painel SLA & Cobranças e redistribua os casos mais antigos."
    if detector == "pico_bairro":
        bairro = (m.get("bairro") or "").strip()
        if bairro and srv:
            return f"Concentre equipe em {bairro}: o serviço «{srv}» concentra os chamados da semana."
        if bairro:
            return f"Verifique no mapa territorial a concentração em {bairro} e ajuste escala se necessário."
    if detector == "inelegibilidade":
        motivo = _truncate_words(str(m.get("motivo_resumo") or ""), 14)
        if motivo:
            return f"Revise regras de elegibilidade relacionadas a «{motivo}» com a equipe de triagem."
        return "Abra o painel de triagem e bloqueios para revisar sessões barradas."
    return "Acompanhe o indicador no destino sugerido e registre a conduta adotada."


def insight_fallback_de_sinal(sinal: dict, escopo_tipo: str) -> dict:
    detector = sinal.get("detector") or "sinal"
    metricas = dict(sinal.get("metricas") or {})
    metricas.setdefault("total", metricas.get("volume_7d") or metricas.get("total_vencidos"))

    evidencia = narrativa_evidencia(detector, metricas)
    recomendacao = narrativa_recomendacao(detector, metricas, escopo_tipo)
    if _PROIBIDO.search(evidencia) or _PROIBIDO.search(recomendacao):
        evidencia = re.sub(r"[^\w\s·,%.-]", "", evidencia)

    return {
        "id": sinal.get("id") or detector,
        "categoria": sinal.get("categoria") or "tendencia_anomalia",
        "severidade": sinal.get("severidade") or "media",
        "titulo": sinal.get("titulo") or "Ponto de atenção",
        "evidencia_numerica": evidencia[:300],
        "recomendacao": recomendacao[:500],
        "acao_sugerida": montar_acao_sugerida(
            detector, escopo_tipo=escopo_tipo, metricas=metricas
        ),
    }


def resumo_executivo_fallback(sinais: list[dict], escopo_tipo: str) -> tuple[str, str]:
    n = len(sinais)
    criticos = sum(1 for s in sinais if s.get("severidade") == "critica")
    altos = sum(1 for s in sinais if s.get("severidade") == "alta")

    escopo = {"controladoria": "município", "ouvidoria": "Ouvidoria", "unidade": "sua secretaria"}.get(
        escopo_tipo, "operação"
    )

    partes = []
    if n == 0:
        texto = f"A operação em {escopo} está estável hoje, sem alertas acima dos limiares configurados."
        return texto, texto

    if criticos:
        partes.append(_plural(criticos, "1 ocorrência crítica", f"{criticos} ocorrências críticas"))
    if altos:
        partes.append(_plural(altos, "1 alerta de alta prioridade", f"{altos} alertas de alta prioridade"))
    detalhe = ", incluindo ".join(partes) if partes else f"{n} pontos de atenção"
    resumo = (
        f"Foram identificados {n} pontos de atenção na {escopo} hoje, {detalhe}. "
        "Leitura gerada pelo motor analítico municipal (sem dados pessoais de cidadãos)."
    )
    titulos = [s.get("titulo", "") for s in sinais[:3]]
    email = "Resumo do dia: " + "; ".join(t for t in titulos if t)
    return resumo, email[:800]