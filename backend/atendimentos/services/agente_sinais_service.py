"""Coleta determinística de fatos operacionais (zero PII) para o Radar Proativo."""

from __future__ import annotations

import copy
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
from atendimentos.services.sla_cobranca_service import sla_vencido
from catalogo.models import EquipamentoPublico, ServicoCatalogo, UnidadeAdministrativa

logger = logging.getLogger(__name__)

_CHAVES_PII = re.compile(
    r"(cpf|cnpj|telefone|celular|email|e-?mail|whatsapp|nome|endereco|endereço|usuario)",
    re.I,
)

ACOES_PADRAO = {
    "mesa_criticos": {
        "label": "Ver críticos na Mesa",
        "rota": "/backoffice/mesa",
        "query": {"urgencia": "critica"},
    },
    "mesa_sugestao_urgencia": {
        "label": "Triagem de urgência IA",
        "rota": "/backoffice/mesa",
        "query": {"apenas_sugestao_urgencia_ia": "true"},
    },
    "setorial": {
        "label": "Painel setorial",
        "rota": "/backoffice/setorial",
        "query": {},
    },
    "sla_cobrancas": {
        "label": "SLA e cobranças",
        "rota": "/backoffice/relatorios/sla-cobrancas",
        "query": {},
    },
}


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
    acao_key: str = "mesa_criticos",
    categoria: str = "tendencia_anomalia",
) -> dict:
    return {
        "detector": detector,
        "categoria": categoria,
        "severidade": severidade,
        "titulo": titulo,
        "metricas": _sanitizar_objeto(metricas),
        "acao_sugerida": copy.deepcopy(ACOES_PADRAO.get(acao_key, ACOES_PADRAO["mesa_criticos"])),
    }


def _detectar_picos_equipamento(
    qs, cfg: ConfiguracaoAgenteGestao, ini_7d, ini_28d, fim
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
        base = int(mapa_base.get(row["equipamento_id"], 0))
        media_sem = (base / 3.0) if base else 0.0
        if media_sem <= 0:
            if atual >= vol_min:
                cresc = 100
            else:
                continue
        else:
            cresc = int(round(100.0 * (atual - media_sem) / media_sem))
        if cresc < pct_min:
            continue
        eq_id = row["equipamento_id"]
        sinais.append(
            _sinal(
                "pico_equipamento",
                "alta" if cresc < 100 else "critica",
                f"Pico em equipamento: {nomes.get(eq_id, str(eq_id)[:8])}",
                {
                    "equipamento_id": str(eq_id),
                    "volume_7d": atual,
                    "media_semanal_ref": round(media_sem, 2),
                    "crescimento_percentual": cresc,
                },
            )
        )
    return sinais[:15]


def _contar_protocolos_por_bairro(qs) -> dict[str, int]:
    buckets: dict[str, int] = {}
    for dados in qs.values_list("dados_dinamicos", flat=True).iterator(chunk_size=300):
        bairro = str((dados or {}).get("bairro") or "").strip()
        if len(bairro) < 2:
            continue
        buckets[bairro] = buckets.get(bairro, 0) + 1
    return buckets


def _detectar_picos_bairro(
    qs, cfg: ConfiguracaoAgenteGestao, ini_7d, ini_28d, fim
) -> list[dict]:
    mapa_7 = _contar_protocolos_por_bairro(qs.filter(data_criacao__gte=ini_7d))
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
        if media_sem <= 0:
            cresc = 100 if atual >= vol_min else 0
        else:
            cresc = int(round(100.0 * (atual - media_sem) / media_sem))
        if cresc < pct_min:
            continue
        sinais.append(
            _sinal(
                "pico_bairro",
                "alta" if cresc < 100 else "critica",
                f"Pico de demanda no bairro: {bairro[:60]}",
                {
                    "bairro": bairro[:80],
                    "volume_7d": atual,
                    "media_semanal_ref": round(media_sem, 2),
                    "crescimento_percentual": cresc,
                },
            )
        )
        if len(sinais) >= 15:
            break
    return sinais


def _detectar_sla_cobranca(qs, agora) -> list[dict]:
    sinais: list[dict] = []
    ativos = qs.exclude(
        status__in=(Protocolo.Status.RESOLVIDO, Protocolo.Status.REJEITADO)
    )
    vencidos = sum(1 for p in ativos[:500] if sla_vencido(p, agora))
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
        sinais.append(
            _sinal(
                "sla_vencido",
                "critica",
                f"{vencidos} protocolo(s) com SLA vencido",
                {"total_vencidos": vencidos},
                acao_key="sla_cobrancas",
                categoria="acao_imediata",
            )
        )
    if alerta_80:
        sinais.append(
            _sinal(
                "sla_preventivo_80",
                "alta",
                f"{alerta_80} protocolo(s) acima de 80% do SLA",
                {"total_acima_80pct": alerta_80},
                acao_key="sla_cobrancas",
            )
        )
    if cobrados:
        sinais.append(
            _sinal(
                "cobranca_cidadao",
                "media",
                f"{cobrados} protocolo(s) com cobrança ao cidadão",
                {"total_com_cobranca": cobrados},
                acao_key="sla_cobrancas",
            )
        )
    return sinais


def _detectar_gargalos_fluxo(qs, cfg: ConfiguracaoAgenteGestao, agora) -> list[dict]:
    sinais: list[dict] = []
    dias = int(cfg.dias_parado_triagem_alerta)
    limite = agora - timedelta(days=dias)
    parados = qs.filter(
        status=Protocolo.Status.EM_ANALISE,
        data_atualizacao__lte=limite,
    ).count()
    revisao = qs.filter(status=Protocolo.Status.AGUARDANDO_REVISAO).count()
    if parados:
        sinais.append(
            _sinal(
                "triagem_parada",
                "alta",
                f"{parados} em análise há {dias}+ dia(s)",
                {"total_em_analise_parado": parados},
            )
        )
    if revisao:
        sinais.append(
            _sinal(
                "aguardando_revisao",
                "media",
                f"{revisao} protocolo(s) aguardando revisão",
                {"total_aguardando_revisao": revisao},
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
                f"{dilig_aguarda} diligência(s) expira(m) em < 24h",
                {"total_expirando_24h": dilig_aguarda},
            )
        )
    dilig_resp = DiligenciaProtocolo.objects.filter(
        status=DiligenciaProtocolo.Status.RESPONDIDA,
        protocolo__in=qs.values("pk"),
    ).count()
    if dilig_resp:
        sinais.append(
            _sinal(
                "diligencia_respondida_pendente",
                "media",
                f"{dilig_resp} diligência(s) respondida(s) aguardando ação",
                {"total_respondidas_sem_acao": dilig_resp},
            )
        )
    return sinais


def _detectar_qualidade(qs) -> list[dict]:
    sinais: list[dict] = []
    kpi = calcular_kpi_retrabalho(qs)
    taxa = float(kpi.get("taxa_retrabalho_percentual") or 0)
    if taxa >= 15:
        sinais.append(
            _sinal(
                "retrabalho_alto",
                "alta",
                f"Taxa de retrabalho em {taxa:.1f}% (30d)",
                {"taxa_retrabalho_percentual": taxa},
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
                f"CSAT médio {float(media_csat):.1f} nos últimos 30 dias",
                {"csat_medio_30d": round(float(media_csat), 2)},
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
            sinais.append(
                _sinal(
                    "servico_retrabalho",
                    "info",
                    f"Retrabalho: {servicos.get(row['servico_id'], 'Serviço')}",
                    {"servico_id": str(row["servico_id"]), "protocolos_reabertos": row["reab"]},
                )
            )
    return sinais[:8]


def _detectar_urgencia_emergencia(qs, agora) -> list[dict]:
    sinais: list[dict] = []
    criticos = qs.filter(
        urgencia=Protocolo.Urgencia.CRITICA,
        status__in=(
            Protocolo.Status.EM_ANALISE,
            Protocolo.Status.EM_ANDAMENTO,
            Protocolo.Status.AGUARDANDO_REVISAO,
        ),
    )
    sem_os = criticos.exclude(ordens_servico__status__in=(
        OrdemServico.Status.EM_ANDAMENTO,
        OrdemServico.Status.PENDENTE,
    )).distinct().count()
    if sem_os:
        sinais.append(
            _sinal(
                "critico_sem_campo",
                "critica",
                f"{sem_os} crítico(s) sem OS em campo",
                {"total_criticos_sem_os": sem_os},
                categoria="acao_imediata",
            )
        )
    sug_pend = qs.filter(urgencia_sugestao_status=Protocolo.UrgenciaSugestaoStatus.PENDENTE).count()
    if sug_pend:
        sinais.append(
            _sinal(
                "sugestao_urgencia_pendente",
                "alta",
                f"{sug_pend} sugestão(ões) de urgência IA pendentes",
                {"total_sugestoes_pendentes": sug_pend},
                acao_key="mesa_sugestao_urgencia",
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
                )
            )
    return sinais


def _detectar_inelegibilidade(escopo_tipo: str, unidade_id: UUID | None, ini_30d) -> list[dict]:
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
        titulo = (row["motivo_inelegibilidade"] or "")[:120]
        if len(titulo) < 5:
            continue
        sinais.append(
            _sinal(
                "inelegibilidade",
                "media",
                f"Inelegibilidade: {titulo[:80]}",
                {"ocorrencias_30d": row["total"], "motivo_hash": hash(titulo) % 10_000},
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
    sinais.extend(_detectar_picos_equipamento(qs, cfg, ini_7d, ini_28d, fim))
    sinais.extend(_detectar_picos_bairro(qs, cfg, ini_7d, ini_28d, fim))
    sinais.extend(_detectar_sla_cobranca(qs, agora))
    sinais.extend(_detectar_gargalos_fluxo(qs, cfg, agora))
    sinais.extend(_detectar_qualidade(qs.filter(data_criacao__gte=ini_30d)))
    sinais.extend(_detectar_urgencia_emergencia(qs, agora))
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