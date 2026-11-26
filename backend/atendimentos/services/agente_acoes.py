"""Rotas e rótulos de ação do Radar — alinhados ao Vue Router (backoffice)."""

from __future__ import annotations

from copy import deepcopy


def _mesa(query: dict | None = None) -> dict:
    return {
        "label": "Abrir Mesa de Trabalho",
        "rota": "/backoffice/mesa-trabalho",
        "query": query or {},
    }


def _setorial(query: dict | None = None) -> dict:
    return {
        "label": "Abrir Painel Setorial",
        "rota": "/backoffice/setorial",
        "query": query or {},
    }


def _mapa(query: dict | None = None) -> dict:
    return {
        "label": "Ver no Mapa Territorial",
        "rota": "/backoffice/dashboard/mapa-gis",
        "query": query or {},
    }


def _inelegibilidade() -> dict:
    return {
        "label": "Abrir painel de Triagem",
        "rota": "/backoffice/dashboard/inelegibilidade",
        "query": {},
    }


def _sla_cobrancas() -> dict:
    return {
        "label": "Abrir SLA & Cobranças",
        "rota": "/backoffice/relatorios/sla-cobrancas",
        "query": {},
    }


def _protocolo(codigo: str) -> dict:
    return {
        "label": f"Abrir {codigo}",
        "rota": f"/backoffice/protocolo/{codigo}",
        "query": {},
    }


def montar_acao_sugerida(
    detector: str,
    *,
    escopo_tipo: str,
    metricas: dict | None = None,
) -> dict:
    """Uma ação distinta por tipo de sinal."""
    m = metricas or {}
    codigos = list(m.get("protocolos_exemplo") or m.get("codigos") or [])[:3]
    bairro = (m.get("bairro") or "").strip()
    equipamento_id = (m.get("equipamento_id") or "").strip()
    busca = " ".join(str(c) for c in codigos if c)

    if detector == "critico_sem_campo":
        if len(codigos) == 1:
            cod = codigos[0]
            return {
                "label": f"Abrir protocolo {cod}",
                "rota": f"/backoffice/protocolo/{cod}",
                "query": {},
            }
        return {
            **_mesa({"urgencia": "critica", "status": "em_analise,em_andamento,aguardando_revisao"}),
            "label": "Abrir críticos na Mesa",
        }
    if detector == "triagem_parada":
        q = {"status": "em_analise"}
        if busca:
            q["busca"] = busca
        return {**_mesa(q), "label": "Revisar fila em análise"}
    if detector == "aguardando_revisao":
        return {**_mesa({"status": "aguardando_revisao"}), "label": "Revisar aguardando homologação"}
    if detector == "diligencia_respondida_pendente":
        if len(codigos) == 1:
            return _protocolo(codigos[0])
        if escopo_tipo == "unidade":
            q = {"busca": busca} if busca else {}
            return {**_setorial(q), "label": "Ver diligências respondidas"}
        q = {"status": "em_analise,em_andamento", "busca": busca} if busca else {"status": "em_analise,em_andamento"}
        return {**_mesa(q), "label": "Ver diligências respondidas"}
    if detector == "diligencia_expirando":
        return {**_mesa({"status": "aguardando_cidadao"}), "label": "Diligências a expirar"}
    if detector == "pico_bairro":
        if not m.get("tem_geo_ocorrencia"):
            q = {}
            if bairro:
                q["bairro"] = bairro
            servicos = m.get("servicos_principais") or []
            if servicos and not q.get("bairro"):
                q["busca"] = str(servicos[0])[:80]
            return {**_mesa(q), "label": "Ver demanda na Mesa"}
        q = {"bairro": bairro} if bairro else {}
        return {**_mapa(q), "label": "Ver no Mapa Territorial"}
    if detector == "pico_equipamento":
        if not m.get("tem_geo_ocorrencia"):
            q = {}
            if equipamento_id:
                q["equipamento_id"] = equipamento_id
            servicos = m.get("servicos_principais") or []
            if servicos:
                q["busca"] = str(servicos[0])[:80]
            return {**_mesa(q), "label": "Ver demanda na Mesa"}
        q = {}
        if equipamento_id:
            q["equipamento_id"] = equipamento_id
        if bairro:
            q["bairro"] = bairro
        return {**_mapa(q), "label": "Ver demanda no mapa"}
    if detector == "inelegibilidade":
        return _inelegibilidade()
    if detector in ("sla_vencido", "sla_preventivo_80", "cobranca_cidadao"):
        return _sla_cobrancas()
    if detector == "sugestao_urgencia_pendente":
        return {
            **_mesa({"apenas_sugestao_urgencia_ia": "true"}),
            "label": "Triagem de urgência IA",
        }
    if detector == "retrabalho_alto":
        return {**_mesa({"apenas_reabertos": "true"}), "label": "Ver protocolos reabertos"}
    if detector == "super_os_volume":
        so_id = (m.get("super_os_id") or "").strip()
        if so_id:
            return {
                "label": "Abrir Super OS",
                "rota": f"/backoffice/super-os/{so_id}",
                "query": {},
            }
    return deepcopy(_mesa())