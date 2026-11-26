"""Catálogo fechado de tools somente leitura do Copiloto Gestor (Sprint 4.7B)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any
from uuid import UUID

from django.db.models import Avg, Count, Q
from django.utils import timezone

from atendimentos.kanban_services import montar_kanban_unificado, resumo_contadores_mesa
from atendimentos.models import CobrancaProtocolo, ConfiguracaoAgenteGestao, Protocolo
from atendimentos.services.agente_acoes import montar_acao_sugerida
from atendimentos.services.agente_sinais_service import OS_EM_CAMPO, _contar_protocolos_por_bairro
from atendimentos.services.analytics_service import (
    STATUS_TMA,
    calcular_kpi_retrabalho,
    calcular_matriz_qualidade_servicos,
    calcular_matriz_qualidade_unidades,
    calcular_ranking_sla_unidades,
    calcular_resumo_sla_mesa,
    calcular_tma_geral,
)
from atendimentos.services.escopo_dados import escopo_dashboard, queryset_protocolos_escopo
from atendimentos.services.inelegibilidade_dashboard_service import dashboard_inelegibilidade
from atendimentos.services.protocolo_geolocalizacao import queryset_geo_ocorrencia_valida
from atendimentos.services.sla_cobranca_service import (
    STATUS_ABERTOS,
    percentual_sla_consumido,
    sla_vencido,
)
from catalogo.models import EquipamentoPublico, UnidadeAdministrativa

NOMES_TOOLS = (
    "obter_resumo_eficiencia",
    "listar_gargalos_sla_e_cobrancas",
    "listar_anomalias_equipamentos_bairros",
    "obter_qualidade_e_retrabalho",
    "resumir_fila_operacional",
    "obter_resumo_inelegibilidade",
)


def referencia_de_acao(acao: dict, tipo: str) -> dict:
    return {
        "label": acao.get("label", "Abrir"),
        "tipo": tipo,
        "rota": acao.get("rota", "/backoffice/mesa-trabalho"),
        "query": acao.get("query") or {},
    }


def _escopo_unidade_id(user, unidade_id: UUID | str | None) -> tuple[UUID | None, str, bool]:
    """
    Retorna (unidade_efetiva, escopo_aplicado, forcou_unidade).
    Gestor setorial: ignora unidade_id divergente.
    """
    escopo = escopo_dashboard(user)
    if escopo["tipo"] == "unidade":
        uid = escopo["unidade_id"]
        forcou = bool(unidade_id and uid and str(unidade_id) != str(uid))
        return uid, "unidade", forcou
    if unidade_id:
        try:
            uid = UUID(str(unidade_id))
            if UnidadeAdministrativa.objects.filter(pk=uid, ativo=True).exists():
                return uid, "municipio", False
        except (TypeError, ValueError):
            pass
    return None, escopo["tipo"], False


def _qs_protocolos(user, *, unidade_id=None, periodo_dias: int | None = None):
    qs = queryset_protocolos_escopo(user)
    uid, _, _ = _escopo_unidade_id(user, unidade_id)
    if uid:
        qs = qs.filter(
            Q(servico__unidade_responsavel_id=uid) | Q(ordens_servico__unidade_id=uid)
        ).distinct()
    if periodo_dias and periodo_dias > 0:
        ini = timezone.now() - timedelta(days=int(periodo_dias))
        qs = qs.filter(data_criacao__gte=ini)
    return qs


def _escopo_tipo_de_usuario(user) -> str:
    from atendimentos.services.agente_persona import resolver_escopo_briefing_usuario

    escopo_tipo, _ = resolver_escopo_briefing_usuario(user, {})
    return escopo_tipo


def obter_resumo_eficiencia(
    user,
    periodo_dias: int = 30,
    unidade_id=None,
) -> dict[str, Any]:
    _, escopo_aplicado, forcou = _escopo_unidade_id(user, unidade_id)
    qs = _qs_protocolos(user, unidade_id=unidade_id, periodo_dias=periodo_dias)
    abertos = qs.filter(status__in=STATUS_ABERTOS).count()
    resolvidos = qs.filter(status__in=STATUS_TMA).count()
    tma = calcular_tma_geral(qs)
    resumo_mesa = calcular_resumo_sla_mesa(user, qs_escopo=qs)
    ranking = calcular_ranking_sla_unidades(qs)[:8]
    refs = []
    if resumo_mesa.get("vencidos", 0) > 0:
        refs.append(
            referencia_de_acao(montar_acao_sugerida("sla_vencido", escopo_tipo=_escopo_tipo_de_usuario(user)), "sla_vencido")
        )
    refs.append(
        referencia_de_acao(
            {"label": "Abrir Dashboard de Eficiência", "rota": "/backoffice/dashboard/eficiencia", "query": {}},
            "dashboard_eficiencia",
        )
    )
    return {
        "periodo_dias": int(periodo_dias),
        "escopo_aplicado": escopo_aplicado,
        "unidade_forcada_escopo": forcou,
        "total_abertos": abertos,
        "total_resolvidos": resolvidos,
        "tma_horas_medio": tma.get("horas"),
        "tma_amostra_resolvidos": tma.get("protocolos_concluidos"),
        "percentual_no_prazo_mesa": resumo_mesa.get("taxa_cumprimento"),
        "itens_mesa_vencidos": resumo_mesa.get("vencidos"),
        "ranking_atraso_secretarias": ranking,
        "referencias_candidatas": refs,
    }


def listar_gargalos_sla_e_cobrancas(
    user,
    unidade_id=None,
    apenas_criticos: bool = False,
    limite: int = 10,
) -> dict[str, Any]:
    _, escopo_aplicado, forcou = _escopo_unidade_id(user, unidade_id)
    qs = queryset_protocolos_escopo(user).filter(status__in=STATUS_ABERTOS)
    uid, _, _ = _escopo_unidade_id(user, unidade_id)
    if uid:
        qs = qs.filter(
            Q(servico__unidade_responsavel_id=uid) | Q(ordens_servico__unidade_id=uid)
        ).distinct()
    if apenas_criticos:
        qs = qs.filter(urgencia=Protocolo.Urgencia.CRITICA)
    agora = timezone.now()
    cobrados_ids = set(
        CobrancaProtocolo.objects.filter(protocolo_id__in=qs.values("pk")).values_list(
            "protocolo_id", flat=True
        )
    )
    itens = []
    codigos_ref = []
    for p in qs.select_related("servico", "servico__unidade_responsavel").iterator(chunk_size=150):
        venc = sla_vencido(p, agora)
        pct = percentual_sla_consumido(p, agora)
        tem_cobranca = p.pk in cobrados_ids
        if not venc and pct < 80 and not tem_cobranca:
            continue
        if apenas_criticos and p.urgencia != Protocolo.Urgencia.CRITICA:
            continue
        dias = max(0, (agora - p.data_criacao).days) if venc else 0
        if venc:
            from atendimentos.services.sla_cobranca_service import dias_atraso

            dias = dias_atraso(p, agora)
        itens.append(
            {
                "codigo": p.codigo,
                "servico": (p.servico.nome if p.servico_id else "—")[:80],
                "urgencia": p.urgencia,
                "sla_vencido": venc,
                "percentual_sla_consumido": round(pct, 1),
                "dias_atraso": dias,
                "tem_cobranca_cidadao": tem_cobranca,
            }
        )
        codigos_ref.append(p.codigo)
        if len(itens) >= max(1, min(int(limite), 50)):
            break
    escopo_tipo = _escopo_tipo_de_usuario(user)
    refs = [
        referencia_de_acao(
            montar_acao_sugerida(
                "sla_vencido",
                escopo_tipo=escopo_tipo,
                metricas={"codigos": codigos_ref[:3]},
            ),
            "sla_vencido",
        )
    ]
    if any(i["tem_cobranca_cidadao"] for i in itens):
        refs.append(referencia_de_acao(montar_acao_sugerida("cobranca_cidadao", escopo_tipo=escopo_tipo), "cobranca_cidadao"))
    return {
        "escopo_aplicado": escopo_aplicado,
        "unidade_forcada_escopo": forcou,
        "total_listados": len(itens),
        "protocolos": itens,
        "referencias_candidatas": refs,
    }


def listar_anomalias_equipamentos_bairros(
    user,
    periodo_dias: int = 14,
    unidade_id=None,
) -> dict[str, Any]:
    cfg = ConfiguracaoAgenteGestao.load()
    _, escopo_aplicado, forcou = _escopo_unidade_id(user, unidade_id)
    fim = timezone.now()
    ini = fim - timedelta(days=max(1, int(periodo_dias)))
    ini_ant = ini - timedelta(days=periodo_dias * 2)
    qs = _qs_protocolos(user, unidade_id=unidade_id)
    qs_geo = queryset_geo_ocorrencia_valida(qs)
    escopo_tipo = _escopo_tipo_de_usuario(user)

    equipamentos = []
    agg_atual = (
        qs_geo.filter(data_criacao__gte=ini, equipamento_id__isnull=False)
        .values("equipamento_id")
        .annotate(total=Count("id"))
    )
    agg_ant = (
        qs_geo.filter(
            data_criacao__gte=ini_ant,
            data_criacao__lt=ini,
            equipamento_id__isnull=False,
        )
        .values("equipamento_id")
        .annotate(total=Count("id"))
    )
    mapa_ant = {r["equipamento_id"]: r["total"] for r in agg_ant}
    pct_min = int(cfg.anomalia_percentual_minimo)
    vol_min = int(cfg.anomalia_volume_minimo)
    for row in agg_atual:
        atual = int(row["total"])
        if atual < vol_min:
            continue
        eq_id = row["equipamento_id"]
        base = int(mapa_ant.get(eq_id, 0))
        media = (base / 2.0) if base else 0.0
        cresc = int(round(100.0 * (atual - media) / media)) if media > 0 else 100
        if media > 0 and cresc < pct_min:
            continue
        nome = (
            EquipamentoPublico.objects.filter(pk=eq_id).values_list("nome", flat=True).first()
            or "Equipamento"
        )
        equipamentos.append(
            {
                "equipamento_id": str(eq_id),
                "nome": nome[:80],
                "volume_periodo": atual,
                "crescimento_percentual_vs_anterior": cresc,
            }
        )

    mapa_bairro = _contar_protocolos_por_bairro(
        queryset_geo_ocorrencia_valida(qs.filter(data_criacao__gte=ini)),
        status_abertos=False,
    )
    mapa_bairro_ant = _contar_protocolos_por_bairro(
        queryset_geo_ocorrencia_valida(
            qs.filter(data_criacao__gte=ini_ant, data_criacao__lt=ini)
        )
    )
    bairros = []
    refs = []
    for bairro, atual in sorted(mapa_bairro.items(), key=lambda x: -x[1])[:12]:
        if atual < vol_min:
            continue
        base = mapa_bairro_ant.get(bairro, 0)
        media = (base / 2.0) if base else 0.0
        cresc = int(round(100.0 * (atual - media) / media)) if media > 0 else 100
        if media > 0 and cresc < pct_min:
            continue
        bairros.append(
            {
                "bairro": bairro[:80],
                "volume_periodo": atual,
                "crescimento_percentual_vs_anterior": cresc,
                "origem_geo_valida": True,
            }
        )
        if len(bairros) <= 3:
            refs.append(
                referencia_de_acao(
                    montar_acao_sugerida(
                        "pico_bairro",
                        escopo_tipo=escopo_tipo,
                        metricas={"bairro": bairro, "tem_geo_ocorrencia": True},
                    ),
                    "pico_bairro",
                )
            )
    if equipamentos:
        eq0 = equipamentos[0]
        refs.append(
            referencia_de_acao(
                montar_acao_sugerida(
                    "pico_equipamento",
                    escopo_tipo=escopo_tipo,
                    metricas={
                        "equipamento_id": eq0["equipamento_id"],
                        "tem_geo_ocorrencia": True,
                    },
                ),
                "pico_equipamento",
            )
        )
    return {
        "periodo_dias": int(periodo_dias),
        "escopo_aplicado": escopo_aplicado,
        "unidade_forcada_escopo": forcou,
        "somente_origem_localizacao_ocorrencia": True,
        "equipamentos_anomalia": equipamentos[:10],
        "bairros_anomalia": bairros[:10],
        "referencias_candidatas": refs,
    }


def obter_qualidade_e_retrabalho(
    user,
    periodo_dias: int = 30,
    unidade_id=None,
) -> dict[str, Any]:
    _, escopo_aplicado, forcou = _escopo_unidade_id(user, unidade_id)
    qs = _qs_protocolos(user, unidade_id=unidade_id, periodo_dias=periodo_dias)
    qs_res = qs.filter(status__in=STATUS_TMA)
    kpi = calcular_kpi_retrabalho(qs)
    media_csat = qs_res.filter(nota_satisfacao__isnull=False).aggregate(m=Avg("nota_satisfacao"))["m"]
    total_aval = qs_res.filter(nota_satisfacao__isnull=False).count()
    matriz_u = calcular_matriz_qualidade_unidades(qs_res)[:8]
    matriz_s = calcular_matriz_qualidade_servicos(qs_res)[:8]
    escopo_tipo = _escopo_tipo_de_usuario(user)
    refs = []
    if float(kpi.get("taxa_retrabalho_percentual") or 0) >= 10:
        refs.append(
            referencia_de_acao(montar_acao_sugerida("retrabalho_alto", escopo_tipo=escopo_tipo), "retrabalho_alto")
        )
    return {
        "periodo_dias": int(periodo_dias),
        "escopo_aplicado": escopo_aplicado,
        "unidade_forcada_escopo": forcou,
        "media_csat": round(float(media_csat), 2) if media_csat is not None else None,
        "total_avaliacoes": total_aval,
        "total_reabertos": kpi.get("total_reabertos"),
        "taxa_retrabalho_percentual": kpi.get("taxa_retrabalho_percentual"),
        "por_secretaria": matriz_u,
        "por_servico": matriz_s,
        "referencias_candidatas": refs,
    }


def resumir_fila_operacional(
    user,
    status=None,
    urgencia=None,
    apenas_sugestao_ia: bool = False,
    apenas_diligencias_respondidas: bool = False,
) -> dict[str, Any]:
    escopo = escopo_dashboard(user)
    params: dict[str, str] = {}
    if status:
        params["status"] = str(status)
    if urgencia:
        params["urgencia"] = str(urgencia)
    if apenas_sugestao_ia:
        params["apenas_sugestao_urgencia_ia"] = "true"
    if apenas_diligencias_respondidas:
        params["apenas_diligencias_respondidas"] = "true"
    itens = montar_kanban_unificado(params, user=user)
    contadores = resumo_contadores_mesa(itens, user=user, params=params)
    escopo_tipo = _escopo_tipo_de_usuario(user)
    qs = queryset_protocolos_escopo(user).filter(status__in=STATUS_ABERTOS)
    parados = qs.filter(status=Protocolo.Status.EM_ANALISE).count()
    revisao = qs.filter(status=Protocolo.Status.AGUARDANDO_REVISAO).count()
    crit_sem_os = (
        qs.filter(urgencia=Protocolo.Urgencia.CRITICA)
        .exclude(ordens_servico__status__in=OS_EM_CAMPO)
        .distinct()
        .count()
    )
    sug_pend = qs.filter(
        urgencia_sugestao_status=Protocolo.UrgenciaSugestaoStatus.PENDENTE,
    ).count()
    refs = [
        referencia_de_acao(montar_acao_sugerida("triagem_parada", escopo_tipo=escopo_tipo), "triagem_parada"),
        referencia_de_acao(montar_acao_sugerida("aguardando_revisao", escopo_tipo=escopo_tipo), "aguardando_revisao"),
    ]
    if crit_sem_os:
        refs.append(
            referencia_de_acao(montar_acao_sugerida("critico_sem_campo", escopo_tipo=escopo_tipo), "critico_sem_campo")
        )
    if sug_pend:
        refs.append(
            referencia_de_acao(
                montar_acao_sugerida("sugestao_urgencia_pendente", escopo_tipo=escopo_tipo),
                "sugestao_urgencia_pendente",
            )
        )
    return {
        "escopo_aplicado": escopo["tipo"],
        "filtros_aplicados": params,
        "total_itens_kanban": len(itens),
        "contadores_mesa": contadores,
        "em_analise": parados,
        "aguardando_revisao": revisao,
        "criticos_sem_os_abertos": crit_sem_os,
        "sugestoes_urgencia_ia_pendentes": sug_pend,
        "referencias_candidatas": refs,
    }


def obter_resumo_inelegibilidade(
    user,
    periodo_dias: int = 30,
) -> dict[str, Any]:
    escopo = escopo_dashboard(user)
    ini = timezone.now() - timedelta(days=max(1, int(periodo_dias)))
    dash = dashboard_inelegibilidade(
        user,
        {
            "data_inicio": ini.date().isoformat(),
        },
    )
    top_servicos = (dash.get("ranking_por_servico") or [])[:5]
    top_motivos = (dash.get("ranking_por_motivo") or [])[:5]
    escopo_tipo = _escopo_tipo_de_usuario(user)
    refs = [referencia_de_acao(montar_acao_sugerida("inelegibilidade", escopo_tipo=escopo_tipo), "inelegibilidade")]
    return {
        "periodo_dias": int(periodo_dias),
        "escopo_aplicado": escopo["tipo"],
        "total_sessoes_bloqueadas": dash.get("total_sessoes_inelegiveis", 0),
        "top_servicos": [
            {"servico_nome": s.get("servico_nome"), "total": s.get("total")} for s in top_servicos
        ],
        "top_motivos": [{"motivo": m.get("motivo"), "total": m.get("total")} for m in top_motivos],
        "referencias_candidatas": refs,
    }


EXECUTORES_TOOLS = {
    "obter_resumo_eficiencia": obter_resumo_eficiencia,
    "listar_gargalos_sla_e_cobrancas": listar_gargalos_sla_e_cobrancas,
    "listar_anomalias_equipamentos_bairros": listar_anomalias_equipamentos_bairros,
    "obter_qualidade_e_retrabalho": obter_qualidade_e_retrabalho,
    "resumir_fila_operacional": resumir_fila_operacional,
    "obter_resumo_inelegibilidade": obter_resumo_inelegibilidade,
}


def executar_tool(nome: str, user, parametros: dict | None = None) -> dict[str, Any]:
    fn = EXECUTORES_TOOLS.get(nome)
    if not fn:
        return {"erro": "tool_desconhecida", "nome": nome, "referencias_candidatas": []}
    params = dict(parametros or {})
    allowed = set(fn.__code__.co_varnames) - {"user"}
    kwargs = {k: v for k, v in params.items() if k in allowed}
    return fn(user, **kwargs)


def catalogo_tools_llm() -> list[dict]:
    return [
        {
            "nome": "obter_resumo_eficiencia",
            "descricao": "Resumo de eficiência: abertos, resolvidos, TMA, % no prazo, ranking secretarias.",
            "parametros": {"periodo_dias": "int 7-90", "unidade_id": "uuid opcional"},
        },
        {
            "nome": "listar_gargalos_sla_e_cobrancas",
            "descricao": "Protocolos vencidos, acima de 80% SLA ou com cobrança ao cidadão (sem PII).",
            "parametros": {"unidade_id": "uuid opcional", "apenas_criticos": "bool", "limite": "int"},
        },
        {
            "nome": "listar_anomalias_equipamentos_bairros",
            "descricao": "Picos por equipamento e bairro (somente geo de ocorrência válida).",
            "parametros": {"periodo_dias": "int", "unidade_id": "uuid opcional"},
        },
        {
            "nome": "obter_qualidade_e_retrabalho",
            "descricao": "CSAT, reaberturas e taxa de retrabalho por secretaria e serviço.",
            "parametros": {"periodo_dias": "int", "unidade_id": "uuid opcional"},
        },
        {
            "nome": "resumir_fila_operacional",
            "descricao": "Foto da fila: análise, revisão, críticos sem OS, sugestões IA, diligências.",
            "parametros": {
                "status": "str opcional",
                "urgencia": "str opcional",
                "apenas_sugestao_ia": "bool",
                "apenas_diligencias_respondidas": "bool",
            },
        },
        {
            "nome": "obter_resumo_inelegibilidade",
            "descricao": "Bloqueios de cidadãos no chat por regra do catálogo.",
            "parametros": {"periodo_dias": "int"},
        },
    ]