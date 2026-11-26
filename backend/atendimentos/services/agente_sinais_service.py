"""Coleta determinística de fatos operacionais (zero PII) para o Radar Proativo."""

from __future__ import annotations

import logging
import re
from datetime import timedelta
from typing import Any
from uuid import UUID

from django.db.models import Avg, Count, F, Q
from django.utils import timezone

from atendimentos.models import (
    BriefingOperacionalIA,
    ConfiguracaoAgenteGestao,
    DiligenciaProtocolo,
    OrdemServico,
    Protocolo,
    SessaoChat,
    SuperOS,
)
from atendimentos.services.analytics_service import calcular_kpi_retrabalho
from atendimentos.services.escopo_dados import q_protocolo_visivel_na_unidade
from atendimentos.services.agente_acoes import montar_acao_sugerida
from atendimentos.services.sla_cobranca_service import STATUS_ABERTOS, sla_vencido
from catalogo.models import EquipamentoPublico, ServicoCatalogo, UnidadeAdministrativa

logger = logging.getLogger(__name__)

_CHAVES_PII = re.compile(
    r"(cpf|cnpj|telefone|celular|email|e-?mail|whatsapp|nome|endereco|endereço|usuario)",
    re.I,
)

OS_EM_CAMPO = frozenset(
    {
        OrdemServico.Status.PENDENTE,
        OrdemServico.Status.EM_ANDAMENTO,
        OrdemServico.Status.AGUARDANDO_FORMALIZACAO,
        OrdemServico.Status.AGUARDANDO_ASSINATURA,
        OrdemServico.Status.AGUARDANDO_CIDADAO,
    }
)


def _truncate_palavras(texto: str, max_palavras: int = 12) -> str:
    partes = (texto or "").split()
    if len(partes) <= max_palavras:
        return (texto or "").strip()
    return " ".join(partes[:max_palavras]).strip() + "…"


def _codigos_protocolo(qs, *, limit: int = 5) -> list[str]:
    return list(qs.order_by("data_atualizacao").values_list("codigo", flat=True)[:limit])


def _servico_top_nome(qs, limit: int = 1) -> list[str]:
    agg = (
        qs.values("servico__nome")
        .annotate(total=Count("id"))
        .order_by("-total")[:limit]
    )
    return [r["servico__nome"] for r in agg if r.get("servico__nome")]


def _sanitizar_objeto(obj: Any) -> Any:
    """Remove chaves que possam carregar PII acidental."""
    if isinstance(obj, dict):
        out = {}
        for chave, valor in obj.items():
            if _CHAVES_PII.search(str(chave)):
                continue
            out[chave] = _sanitizar_objeto(valor)
        return out
    if isinstance(obj, list):
        return [_sanitizar_objeto(v) for v in obj]
    if isinstance(obj, str) and len(obj) > 500:
        return obj[:500]
    return obj


def _qs_protocolos_escopo(
    escopo_tipo: str,
    unidade_id: UUID | None,
):
    qs = Protocolo.objects.select_related("servico", "servico__unidade_responsavel")
    if escopo_tipo == BriefingOperacionalIA.EscopoTipo.UNIDADE and unidade_id:
        qs = qs.filter(q_protocolo_visivel_na_unidade(unidade_id)).distinct()
    return qs


def _janela(now):
    fim = now
    ini_7d = fim - timedelta(days=7)
    ini_28d = fim - timedelta(days=28)
    ini_30d = fim - timedelta(days=30)
    return ini_7d, ini_28d, ini_30d, fim


def _sinal(
    detector: str,
    severidade: str,
    titulo: str,
    metricas: dict,
    *,
    escopo_tipo: str,
    categoria: str = "tendencia_anomalia",
) -> dict:
    metricas = _sanitizar_objeto(metricas)
    return {
        "id": detector,
        "detector": detector,
        "categoria": categoria,
        "severidade": severidade,
        "titulo": titulo,
        "metricas": metricas,
        "acao_sugerida": montar_acao_sugerida(
            detector, escopo_tipo=escopo_tipo, metricas=metricas
        ),
    }


def _detectar_picos_equipamento(
    qs, cfg: ConfiguracaoAgenteGestao, ini_7d, ini_28d, fim, escopo_tipo: str
) -> list[dict]:
    sinais: list[dict] = []
    agg_7 = (
        qs.filter(data_criacao__gte=ini_7d, equipamento_id__isnull=False)
        .values("equipamento_id")
        .annotate(total=Count("id"))
    )
    agg_base = (
        qs.filter(
            data_criacao__gte=ini_28d,
            data_criacao__lt=ini_7d,
            equipamento_id__isnull=False,
        )
        .values("equipamento_id")
        .annotate(total=Count("id"))
    )
    mapa_base = {r["equipamento_id"]: r["total"] for r in agg_base}
    nomes = {
        e.id: e.nome
        for e in EquipamentoPublico.objects.filter(
            pk__in=[r["equipamento_id"] for r in agg_7]
        ).only("id", "nome")
    }
    pct_min = int(cfg.anomalia_percentual_minimo)
    vol_min = int(cfg.anomalia_volume_minimo)
    for row in agg_7:
        atual = int(row["total"])
        if atual < vol_min:
            continue
        eq_id = row["equipamento_id"]
        qs_eq = qs.filter(
            equipamento_id=eq_id,
            data_criacao__gte=ini_7d,
            status__in=STATUS_ABERTOS,
        )
        abertos = qs_eq.count()
        if abertos < vol_min and atual < vol_min:
            continue
        base = int(mapa_base.get(eq_id, 0))
        media_sem = (base / 3.0) if base else 0.0
        novo_foco = media_sem <= 0
        cresc = 0
        if not novo_foco:
            cresc = int(round(100.0 * (atual - media_sem) / media_sem))
            if cresc < pct_min:
                continue
        nome_eq = nomes.get(eq_id, "Equipamento")
        titulo = (
            f"Novo foco de demanda: {nome_eq[:60]}"
            if novo_foco
            else f"Pico em equipamento: {nome_eq[:60]}"
        )
        servicos = _servico_top_nome(qs_eq)
        sinais.append(
            _sinal(
                "pico_equipamento",
                "alta" if novo_foco or cresc < 100 else "critica",
                titulo,
                {
                    "equipamento_id": str(eq_id),
                    "volume_7d": atual,
                    "crescimento_percentual": cresc,
                    "novo_foco": novo_foco,
                    "servicos_principais": servicos,
                    "protocolos_exemplo": _codigos_protocolo(qs_eq),
                },
                escopo_tipo=escopo_tipo,
            )
        )
    return sinais[:15]


def _contar_protocolos_por_bairro(qs, *, status_abertos: bool = False) -> dict[str, int]:
    if status_abertos:
        qs = qs.filter(status__in=STATUS_ABERTOS)
    buckets: dict[str, int] = {}
    for dados in qs.values_list("dados_dinamicos", flat=True).iterator(chunk_size=300):
        bairro = str((dados or {}).get("bairro") or "").strip()
        if len(bairro) < 2:
            continue
        buckets[bairro] = buckets.get(bairro, 0) + 1
    return buckets


def _detectar_picos_bairro(
    qs, cfg: ConfiguracaoAgenteGestao, ini_7d, ini_28d, fim, escopo_tipo: str
) -> list[dict]:
    mapa_7 = _contar_protocolos_por_bairro(
        qs.filter(data_criacao__gte=ini_7d), status_abertos=True
    )
    mapa_base = _contar_protocolos_por_bairro(
        qs.filter(data_criacao__gte=ini_28d, data_criacao__lt=ini_7d)
    )
    pct_min = int(cfg.anomalia_percentual_minimo)
    vol_min = int(cfg.anomalia_volume_minimo)
    sinais: list[dict] = []
    for bairro, atual in sorted(mapa_7.items(), key=lambda x: -x[1]):
        if atual < vol_min:
            continue
        base = mapa_base.get(bairro, 0)
        media_sem = (base / 3.0) if base else 0.0
        novo_foco = media_sem <= 0
        cresc = 0
        if not novo_foco:
            cresc = int(round(100.0 * (atual - media_sem) / media_sem))
            if cresc < pct_min:
                continue
        qs_bairro = qs.filter(
            data_criacao__gte=ini_7d,
            status__in=STATUS_ABERTOS,
        ).filter(
            Q(dados_dinamicos__bairro__iexact=bairro)
            | Q(dados_dinamicos__bairro__icontains=bairro)
        )
        servicos = _servico_top_nome(qs_bairro)
        titulo = (
            f"Novo foco de demanda no bairro {bairro[:50]}"
            if novo_foco
            else f"Pico de demanda no bairro: {bairro[:50]}"
        )
        sinais.append(
            _sinal(
                "pico_bairro",
                "alta" if novo_foco or cresc < 100 else "critica",
                titulo,
                {
                    "bairro": bairro[:80],
                    "volume_7d": atual,
                    "crescimento_percentual": cresc,
                    "novo_foco": novo_foco,
                    "servicos_principais": servicos,
                    "protocolos_exemplo": _codigos_protocolo(qs_bairro),
                },
                escopo_tipo=escopo_tipo,
            )
        )
        if len(sinais) >= 15:
            break
    return sinais


def _detectar_sla_cobranca(qs, agora, escopo_tipo: str) -> list[dict]:
    sinais: list[dict] = []
    ativos = qs.filter(status__in=STATUS_ABERTOS)
    vencidos_qs = [p for p in ativos[:500] if sla_vencido(p, agora)]
    vencidos = len(vencidos_qs)
    alerta_80 = 0
    for p in ativos.filter(prazo_sla__isnull=False)[:500]:
        if not p.prazo_sla:
            continue
        total = (p.prazo_sla - p.data_criacao).total_seconds()
        if total <= 0:
            continue
        decorrido = (agora - p.data_criacao).total_seconds()
        if decorrido / total >= 0.8 and not sla_vencido(p, agora):
            alerta_80 += 1
    cobrados = ativos.filter(qtd_cobrancas_cidadao__gte=1).count()
    if vencidos:
        codigos = [p.codigo for p in vencidos_qs[:5]]
        sinais.append(
            _sinal(
                "sla_vencido",
                "critica",
                f"{vencidos} protocolos com SLA vencido",
                {"total_vencidos": vencidos, "protocolos_exemplo": codigos},
                escopo_tipo=escopo_tipo,
                categoria="acao_imediata",
            )
        )
    if alerta_80:
        sinais.append(
            _sinal(
                "sla_preventivo_80",
                "alta",
                f"{alerta_80} protocolos acima de 80% do SLA",
                {"total_acima_80pct": alerta_80},
                escopo_tipo=escopo_tipo,
            )
        )
    if cobrados:
        sinais.append(
            _sinal(
                "cobranca_cidadao",
                "media",
                f"{cobrados} protocolos com cobrança do cidadão",
                {"total_com_cobranca": cobrados},
                escopo_tipo=escopo_tipo,
            )
        )
    return sinais


def _detectar_gargalos_fluxo(
    qs, cfg: ConfiguracaoAgenteGestao, agora, escopo_tipo: str
) -> list[dict]:
    sinais: list[dict] = []
    dias = int(cfg.dias_parado_triagem_alerta)
    limite = agora - timedelta(days=dias)
    parados_qs = qs.filter(status=Protocolo.Status.EM_ANALISE).filter(
        Q(data_atualizacao__lte=limite) | Q(data_criacao__lte=limite)
    )
    parados = parados_qs.count()
    dias_max = 0
    if parados:
        mais_antigo = parados_qs.order_by("data_atualizacao").first()
        if mais_antigo:
            ref = mais_antigo.data_atualizacao or mais_antigo.data_criacao
            dias_max = max(0, (agora - ref).days)
    revisao_qs = qs.filter(status=Protocolo.Status.AGUARDANDO_REVISAO)
    revisao = revisao_qs.count()
    if parados:
        sinais.append(
            _sinal(
                "triagem_parada",
                "alta",
                f"{parados} protocolos parados na triagem há mais de {dias} dias",
                {
                    "total_em_analise_parado": parados,
                    "dias_parado_max": dias_max,
                    "protocolos_exemplo": _codigos_protocolo(parados_qs),
                    "servicos_principais": _servico_top_nome(parados_qs),
                },
                escopo_tipo=escopo_tipo,
                categoria="acao_imediata",
            )
        )
    if revisao:
        sinais.append(
            _sinal(
                "aguardando_revisao",
                "media",
                f"{revisao} protocolos aguardando revisão",
                {
                    "total_aguardando_revisao": revisao,
                    "protocolos_exemplo": _codigos_protocolo(revisao_qs),
                },
                escopo_tipo=escopo_tipo,
            )
        )
    expira = agora + timedelta(hours=24)
    dilig_aguarda = DiligenciaProtocolo.objects.filter(
        status=DiligenciaProtocolo.Status.AGUARDANDO_CIDADAO,
        prazo_resposta__lte=expira,
        protocolo__in=qs.values("pk"),
    ).count()
    if dilig_aguarda:
        sinais.append(
            _sinal(
                "diligencia_expirando",
                "alta",
                f"{dilig_aguarda} diligências expiram em menos de 24 horas",
                {"total_expirando_24h": dilig_aguarda},
                escopo_tipo=escopo_tipo,
            )
        )
    from django.db.models import Exists, OuterRef

    os_concluida_apos = OrdemServico.objects.filter(
        protocolo_id=OuterRef("protocolo_id"),
        status=OrdemServico.Status.CONCLUIDA,
        concluido_em__isnull=False,
        concluido_em__gt=OuterRef("respondida_em"),
    )
    dilig_resp_qs = (
        DiligenciaProtocolo.objects.filter(
            status=DiligenciaProtocolo.Status.RESPONDIDA,
            protocolo__status__in=STATUS_ABERTOS,
            protocolo_id__in=qs.values("pk"),
            respondida_em__isnull=False,
        )
        .exclude(Exists(os_concluida_apos))
        .select_related("protocolo", "protocolo__servico", "unidade_solicitante")
    )
    dilig_resp = dilig_resp_qs.count()
    if dilig_resp:
        codigos = list(
            dilig_resp_qs.values_list("protocolo__codigo", flat=True).distinct()[:5]
        )
        unidades = list(
            dilig_resp_qs.values_list("unidade_solicitante__nome", flat=True).distinct()[:2]
        )
        sinais.append(
            _sinal(
                "diligencia_respondida_pendente",
                "media",
                f"{dilig_resp} diligências respondidas aguardando ação da equipe",
                {
                    "total_respondidas_pendentes": dilig_resp,
                    "protocolos_exemplo": codigos,
                    "unidades": unidades,
                },
                escopo_tipo=escopo_tipo,
                categoria="acao_imediata",
            )
        )
    return sinais


def _detectar_qualidade(qs, escopo_tipo: str) -> list[dict]:
    sinais: list[dict] = []
    kpi = calcular_kpi_retrabalho(qs)
    taxa = float(kpi.get("taxa_retrabalho_percentual") or 0)
    if taxa >= 15:
        sinais.append(
            _sinal(
                "retrabalho_alto",
                "alta",
                f"Taxa de retrabalho em {taxa:.1f}% nos últimos 30 dias",
                {"taxa_retrabalho_percentual": round(taxa, 1)},
                escopo_tipo=escopo_tipo,
            )
        )
    media_csat = qs.filter(
        nota_satisfacao__isnull=False,
        data_atualizacao__gte=timezone.now() - timedelta(days=30),
    ).aggregate(m=Avg("nota_satisfacao"))["m"]
    if media_csat is not None and float(media_csat) < 3.5:
        sinais.append(
            _sinal(
                "csat_baixo",
                "media",
                f"Índice de satisfação médio {float(media_csat):.1f} nos últimos 30 dias",
                {"csat_medio_30d": round(float(media_csat), 2)},
                escopo_tipo=escopo_tipo,
            )
        )
    por_servico = (
        qs.filter(qtd_reaberturas__gte=1)
        .values("servico_id")
        .annotate(reab=Count("id"))
        .order_by("-reab")[:5]
    )
    if por_servico:
        servicos = {
            s.id: s.nome
            for s in ServicoCatalogo.objects.filter(pk__in=[r["servico_id"] for r in por_servico])
        }
        for row in por_servico:
            nome = servicos.get(row["servico_id"], "Serviço")
            sinais.append(
                _sinal(
                    "servico_retrabalho",
                    "info",
                    f"Retrabalho concentrado: {nome[:60]}",
                    {
                        "servico_nome": nome,
                        "protocolos_reabertos": row["reab"],
                    },
                    escopo_tipo=escopo_tipo,
                )
            )
    return sinais[:8]


def _detectar_urgencia_emergencia(qs, agora, escopo_tipo: str) -> list[dict]:
    sinais: list[dict] = []
    criticos_qs = qs.filter(
        urgencia=Protocolo.Urgencia.CRITICA,
        status__in=STATUS_ABERTOS,
    )
    sem_os_qs = criticos_qs.exclude(
        ordens_servico__status__in=OS_EM_CAMPO
    ).distinct()
    sem_os = sem_os_qs.count()
    if sem_os:
        sinais.append(
            _sinal(
                "critico_sem_campo",
                "critica",
                f"{sem_os} protocolos críticos sem ordem de serviço em campo",
                {
                    "total_criticos_sem_os": sem_os,
                    "protocolos_exemplo": _codigos_protocolo(sem_os_qs),
                    "servicos_principais": _servico_top_nome(sem_os_qs),
                },
                escopo_tipo=escopo_tipo,
                categoria="acao_imediata",
            )
        )
    sug_pend = qs.filter(
        urgencia_sugestao_status=Protocolo.UrgenciaSugestaoStatus.PENDENTE,
        status__in=STATUS_ABERTOS,
    ).count()
    if sug_pend:
        sinais.append(
            _sinal(
                "sugestao_urgencia_pendente",
                "alta",
                f"{sug_pend} sugestões de urgência IA aguardando revisão",
                {"total_sugestoes_pendentes": sug_pend},
                escopo_tipo=escopo_tipo,
            )
        )
    super_abertas = SuperOS.objects.filter(
        status__in=(
            Protocolo.Status.EM_ANALISE,
            Protocolo.Status.EM_ANDAMENTO,
        )
    ).annotate(qtd=Count("protocolos_filhos"))
    for so in super_abertas[:10]:
        qtd = int(so.qtd or 0)
        if qtd >= 10:
            sinais.append(
                _sinal(
                    "super_os_volume",
                    "alta" if qtd < 15 else "critica",
                    f"Super OS {so.codigo} com {qtd} protocolos vinculados",
                    {"super_os_id": str(so.id), "protocolos_vinculados": qtd},
                    escopo_tipo=escopo_tipo,
                )
            )
    return sinais


def _detectar_inelegibilidade(
    escopo_tipo: str, unidade_id: UUID | None, ini_30d
) -> list[dict]:
    qs = SessaoChat.objects.filter(
        motivo_inelegibilidade__isnull=False,
        atualizado_em__gte=ini_30d,
    ).exclude(motivo_inelegibilidade="")
    if escopo_tipo == BriefingOperacionalIA.EscopoTipo.UNIDADE and unidade_id:
        from atendimentos.services.escopo_dados import q_sessao_chat_visivel_na_unidade

        qs = qs.filter(q_sessao_chat_visivel_na_unidade(unidade_id))
    agrupado = (
        qs.values("motivo_inelegibilidade")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )
    sinais = []
    for row in agrupado:
        motivo_raw = (row["motivo_inelegibilidade"] or "").strip()
        if len(motivo_raw) < 5:
            continue
        resumo = _truncate_palavras(motivo_raw, 12)
        sinais.append(
            _sinal(
                "inelegibilidade",
                "media",
                f"Bloqueios por regra: {resumo}",
                {"ocorrencias_30d": row["total"], "motivo_resumo": resumo},
                escopo_tipo=escopo_tipo,
                categoria="sugestao_conducao",
            )
        )
    return sinais


def coletar_fatos_operacionais(
    escopo_tipo: str,
    *,
    unidade: UnidadeAdministrativa | None = None,
    config: ConfiguracaoAgenteGestao | None = None,
) -> dict[str, Any]:
    cfg = config or ConfiguracaoAgenteGestao.load()
    unidade_id = unidade.pk if unidade else None
    agora = timezone.now()
    ini_7d, ini_28d, ini_30d, fim = _janela(agora)
    qs = _qs_protocolos_escopo(escopo_tipo, unidade_id)

    sinais: list[dict] = []
    sinais.extend(_detectar_picos_equipamento(qs, cfg, ini_7d, ini_28d, fim, escopo_tipo))
    sinais.extend(_detectar_picos_bairro(qs, cfg, ini_7d, ini_28d, fim, escopo_tipo))
    sinais.extend(_detectar_sla_cobranca(qs, agora, escopo_tipo))
    sinais.extend(_detectar_gargalos_fluxo(qs, cfg, agora, escopo_tipo))
    sinais.extend(_detectar_qualidade(qs.filter(data_criacao__gte=ini_30d), escopo_tipo))
    sinais.extend(_detectar_urgencia_emergencia(qs, agora, escopo_tipo))
    sinais.extend(_detectar_inelegibilidade(escopo_tipo, unidade_id, ini_30d))

    payload = {
        "versao": "deterministico_v1",
        "gerado_em": agora.isoformat(),
        "escopo_tipo": escopo_tipo,
        "unidade_id": str(unidade_id) if unidade_id else None,
        "unidade_nome": unidade.nome if unidade else None,
        "parametros": {
            "anomalia_percentual_minimo": cfg.anomalia_percentual_minimo,
            "anomalia_volume_minimo": cfg.anomalia_volume_minimo,
            "dias_parado_triagem_alerta": cfg.dias_parado_triagem_alerta,
        },
        "sinais": sinais,
    }
    return _sanitizar_objeto(payload)