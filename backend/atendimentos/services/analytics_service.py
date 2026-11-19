"""Analytics de eficiência — agregações ORM (Process Mining / SLA)."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import timedelta
from typing import Any
from django.db.models import (
    Avg,
    Case,
    Count,
    DateTimeField,
    DurationField,
    F,
    IntegerField,
    Q,
    Sum,
    When,
)
from django.db.models.expressions import ExpressionWrapper
from django.db.models.functions import Now
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from atendimentos.kanban_services import montar_kanban_unificado
from atendimentos.models import OrdemServico, Protocolo, SuperOS
from atendimentos.services.dashboard_filters import aplicar_filtro_bairro
from atendimentos.services.csat_service import calcular_resumo_csat
from atendimentos.services.escopo_dados import escopo_dashboard, queryset_protocolos_escopo

SEM_UNIDADE_ID = "sem-secretaria-vinculada"

# Encerramento operacional (SLA: data de fechamento efetiva).
STATUS_ENCERRADOS = frozenset(
    {
        Protocolo.Status.RESOLVIDO,
        Protocolo.Status.REJEITADO,
    }
)

# TMA — apenas atendimentos concluídos com êxito (rejeições ficam fora da média).
STATUS_TMA = frozenset({Protocolo.Status.RESOLVIDO})

LABELS_FUNIL = {
    Protocolo.Status.EM_ANALISE: "Em análise",
    Protocolo.Status.EM_ANDAMENTO: "Em andamento",
    Protocolo.Status.AGUARDANDO_REVISAO: "Aguardando revisão",
    Protocolo.Status.RESOLVIDO: "Resolvido",
    Protocolo.Status.REJEITADO: "Rejeitado",
}


def _protocolos_anotados_sla(qs):
    """Anota prazo SLA e flag vencido — mesma regra da Mesa (``calcular_sla``)."""
    qs = qs.annotate(
        _prazo_sla=ExpressionWrapper(
            F("data_criacao")
            + timedelta(hours=1) * F("servico__sla_horas"),
            output_field=DateTimeField(),
        )
    )
    return qs.annotate(
        _vencido_flag=Case(
            When(_prazo_sla__lt=Now(), then=1),
            default=0,
            output_field=IntegerField(),
        ),
        _duracao_atendimento=Case(
            When(
                status__in=STATUS_TMA,
                then=ExpressionWrapper(
                    F("data_atualizacao") - F("data_criacao"),
                    output_field=DurationField(),
                ),
            ),
            default=None,
            output_field=DurationField(),
        ),
    )


def _duration_to_horas(delta) -> float | None:
    if delta is None:
        return None
    if hasattr(delta, "total_seconds"):
        return round(delta.total_seconds() / 3600.0, 2)
    return None


def calcular_tma_geral(qs) -> dict[str, Any]:
    resolvidos = qs.filter(status__in=STATUS_TMA)
    agg = resolvidos.aggregate(
        media=Avg(
            ExpressionWrapper(
                F("data_atualizacao") - F("data_criacao"),
                output_field=DurationField(),
            )
        ),
        total=Count("id"),
    )
    return {
        "horas": _duration_to_horas(agg["media"]),
        "protocolos_concluidos": int(agg["total"] or 0),
    }


def calcular_funil_status(qs) -> list[dict[str, Any]]:
    rows = (
        qs.values("status")
        .annotate(total=Count("id"))
        .order_by("status")
    )
    out = []
    for row in rows:
        status = row["status"]
        out.append(
            {
                "status": status,
                "label": LABELS_FUNIL.get(status, status),
                "total": int(row["total"] or 0),
            }
        )
    return out


def resolver_unidade_operacional(protocolo: Protocolo) -> tuple[str, str, str]:
    """
    Secretaria/setor operacional: catálogo → OS ativa → bucket explícito de governança.
    """
    if protocolo.servico_id and protocolo.servico.unidade_responsavel_id:
        u = protocolo.servico.unidade_responsavel
        return str(u.id), u.nome, (u.sigla or "").strip()

    ordem = (
        protocolo.ordens_servico.exclude(status=OrdemServico.Status.CANCELADA)
        .select_related("unidade")
        .order_by("-criado_em")
        .first()
    )
    if ordem and ordem.unidade_id:
        u = ordem.unidade
        return str(u.id), u.nome, (u.sigla or "").strip()

    return (
        SEM_UNIDADE_ID,
        "Sem secretaria vinculada",
        "—",
    )


def resolver_unidade_super_os(filhos: list[Protocolo]) -> tuple[str, str, str]:
    if not filhos:
        return SEM_UNIDADE_ID, "Sem secretaria vinculada", "—"
    atribuicoes = [resolver_unidade_operacional(p) for p in filhos]
    contagem = Counter(a[0] for a in atribuicoes)
    escolhido = contagem.most_common(1)[0][0]
    for uid, nome, sigla in atribuicoes:
        if uid == escolhido:
            return uid, nome, sigla
    return atribuicoes[0]


def _itens_mesa_visiveis(user, qs_escopo=None) -> list[dict]:
    qs = qs_escopo if qs_escopo is not None else queryset_protocolos_escopo(user)
    ids_escopo = {str(pk) for pk in qs.values_list("id", flat=True)}
    itens = montar_kanban_unificado({}, user=user)
    visiveis: list[dict] = []
    for item in itens:
        if item.get("tipo") == "protocolo":
            if item.get("id") in ids_escopo:
                visiveis.append(item)
            continue
        if item.get("tipo") == "super_os":
            if qs.filter(super_os_id=item.get("id")).exists():
                visiveis.append(item)
    return visiveis


def _query_params_dict(query_params) -> dict:
    if query_params is None:
        return {}
    if hasattr(query_params, "dict"):
        return {k: query_params.get(k) for k in query_params.keys()}
    return dict(query_params)


def _tma_horas_protocolos(protocolos: list[Protocolo]) -> float | None:
    duracoes = []
    for p in protocolos:
        if p.status not in STATUS_TMA:
            continue
        if not p.data_atualizacao or not p.data_criacao:
            continue
        duracoes.append(p.data_atualizacao - p.data_criacao)
    if not duracoes:
        return None
    media = sum((d.total_seconds() for d in duracoes), 0.0) / len(duracoes)
    return round(media / 3600.0, 2)


def calcular_ranking_gargalos_mesa(
    user, qs_escopo=None
) -> list[dict[str, Any]]:
    """
    Ranking por secretaria com base nos cartões da Mesa (mesma base do resumo SLA).
    Atribuição: servico.unidade_responsavel ou unidade da OS; senão bucket de alerta.
    """
    visiveis = _itens_mesa_visiveis(user, qs_escopo=qs_escopo)
    if not visiveis:
        return []

    protocolo_ids = [item["id"] for item in visiveis if item.get("tipo") == "protocolo"]
    super_ids = [item["id"] for item in visiveis if item.get("tipo") == "super_os"]

    protos_map = {
        str(p.id): p
        for p in Protocolo.objects.filter(id__in=protocolo_ids)
        .select_related("servico", "servico__unidade_responsavel")
        .prefetch_related("ordens_servico__unidade")
    }
    super_map = {
        str(s.id): s
        for s in SuperOS.objects.filter(id__in=super_ids).prefetch_related(
            "protocolos_filhos__servico",
            "protocolos_filhos__servico__unidade_responsavel",
            "protocolos_filhos__ordens_servico__unidade",
        )
    }

    buckets: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "nome": "",
            "sigla": "",
            "total": 0,
            "vencidos": 0,
            "protocolos_tma": [],
        }
    )

    for item in visiveis:
        vencido = bool((item.get("sla") or {}).get("vencido"))
        if item.get("tipo") == "protocolo":
            proto = protos_map.get(item["id"])
            if not proto:
                continue
            uid, nome, sigla = resolver_unidade_operacional(proto)
            buckets[uid]["protocolos_tma"].append(proto)
        else:
            sos = super_map.get(item["id"])
            filhos = list(sos.protocolos_filhos.all()) if sos else []
            uid, nome, sigla = resolver_unidade_super_os(filhos)
            buckets[uid]["protocolos_tma"].extend(filhos)

        buckets[uid]["nome"] = nome
        buckets[uid]["sigla"] = sigla
        buckets[uid]["total"] += 1
        if vencido:
            buckets[uid]["vencidos"] += 1

    ranking: list[dict[str, Any]] = []
    for uid, agg in buckets.items():
        total = int(agg["total"] or 0)
        if total <= 0:
            continue
        vencidos = int(agg["vencidos"] or 0)
        no_prazo = max(0, total - vencidos)
        pct_vencidos = round(100.0 * vencidos / total, 2)
        pct_no_prazo = round(100.0 * no_prazo / total, 2)
        ranking.append(
            {
                "unidade_id": uid,
                "nome": agg["nome"] or "",
                "sigla": agg["sigla"] or "",
                "total_protocolos": total,
                "pct_no_prazo": pct_no_prazo,
                "pct_vencidos": pct_vencidos,
                "tma_horas": _tma_horas_protocolos(agg["protocolos_tma"]),
                "protocolos_concluidos": sum(
                    1 for p in agg["protocolos_tma"] if p.status in STATUS_TMA
                ),
                "sem_vinculo_catalogo": uid == SEM_UNIDADE_ID,
            }
        )

    ranking.sort(key=lambda x: (x["pct_vencidos"], x["total_protocolos"]), reverse=True)
    return ranking


def calcular_ranking_sla_unidades(qs) -> list[dict[str, Any]]:
    """Ranking legado por ``servico.unidade_responsavel`` (ORM bruto)."""
    base = _protocolos_anotados_sla(
        qs.filter(servico__unidade_responsavel__isnull=False)
    )
    grouped = (
        base.values(
            "servico__unidade_responsavel_id",
            "servico__unidade_responsavel__nome",
            "servico__unidade_responsavel__sigla",
        )
        .annotate(
            total_protocolos=Count("id"),
            vencidos=Sum("_vencido_flag"),
            tma_medio=Avg(
                "_duracao_atendimento",
                filter=Q(status__in=STATUS_TMA),
            ),
            concluidos=Count("id", filter=Q(status__in=STATUS_TMA)),
        )
        .order_by("-vencidos", "-total_protocolos")
    )

    ranking = []
    for row in grouped:
        total = int(row["total_protocolos"] or 0)
        vencidos = int(row["vencidos"] or 0)
        if total <= 0:
            continue
        no_prazo = max(0, total - vencidos)
        pct_vencidos = round(100.0 * vencidos / total, 2)
        pct_no_prazo = round(100.0 * no_prazo / total, 2)
        ranking.append(
            {
                "unidade_id": str(row["servico__unidade_responsavel_id"]),
                "nome": row["servico__unidade_responsavel__nome"] or "",
                "sigla": row["servico__unidade_responsavel__sigla"] or "",
                "total_protocolos": total,
                "pct_no_prazo": pct_no_prazo,
                "pct_vencidos": pct_vencidos,
                "tma_horas": _duration_to_horas(row["tma_medio"]),
                "protocolos_concluidos": int(row["concluidos"] or 0),
            }
        )

    ranking.sort(key=lambda x: (x["pct_vencidos"], -x["total_protocolos"]), reverse=True)
    return ranking


def calcular_resumo_sla_mesa(user, qs_escopo=None) -> dict[str, Any]:
    """
    Resumo de SLA alinhado aos contadores da Mesa (Kanban unificado).
    Conta cartões visíveis (protocolos sem Super OS + incidentes Super OS), não filhos agregados.
    """
    visiveis = _itens_mesa_visiveis(user, qs_escopo=qs_escopo)
    total = len(visiveis)
    vencidos = sum(1 for i in visiveis if (i.get("sla") or {}).get("vencido"))
    no_prazo = max(0, total - vencidos)
    taxa = round(100.0 * no_prazo / total, 2) if total else 0.0
    return {
        "total_itens": total,
        "vencidos": vencidos,
        "no_prazo": no_prazo,
        "taxa_cumprimento": taxa,
    }


def dashboard_eficiencia(user, query_params=None) -> dict[str, Any]:
    """Payload completo do dashboard de eficiência."""
    escopo = escopo_dashboard(user)
    params = _query_params_dict(query_params)
    qs = queryset_protocolos_escopo(user)
    qs, bairro = aplicar_filtro_bairro(qs, params.get("bairro"))
    resumo_mesa = calcular_resumo_sla_mesa(user, qs_escopo=qs)

    filtros_aplicados: dict[str, Any] = {}
    if bairro:
        filtros_aplicados["bairro"] = bairro

    return {
        "escopo": escopo["tipo"],
        "unidade_id": str(escopo["unidade_id"]) if escopo["unidade_id"] else None,
        "gerado_em": timezone.now().isoformat(),
        "filtros_aplicados": filtros_aplicados,
        "tma_geral": calcular_tma_geral(qs),
        "funil_status": calcular_funil_status(qs),
        "ranking_sla_unidades": calcular_ranking_gargalos_mesa(user, qs_escopo=qs),
        "resumo_sla_mesa": resumo_mesa,
        "totais": {
            "protocolos": qs.count(),
            "itens_mesa": resumo_mesa["total_itens"],
        },
    }


def calcular_matriz_qualidade_unidades(qs) -> list[dict[str, Any]]:
    """
    Agrega protocolos RESOLVIDO por servico.unidade_responsavel.
    SLA cumprido: data_atualizacao <= prazo (criação + servico.sla_horas).
    Satisfação: média real de ``AvaliacaoProtocolo`` (OneToOne).
    """
    base = qs.filter(status__in=STATUS_TMA).annotate(
        _prazo_sla=ExpressionWrapper(
            F("data_criacao")
            + timedelta(hours=1) * F("servico__sla_horas"),
            output_field=DateTimeField(),
        )
    ).annotate(
        _cumprido_sla=Case(
            When(
                data_atualizacao__lte=F("_prazo_sla"),
                then=1,
            ),
            default=0,
            output_field=IntegerField(),
        )
    )

    grouped = (
        base.values(
            "servico__unidade_responsavel_id",
            "servico__unidade_responsavel__nome",
            "servico__unidade_responsavel__sigla",
        )
        .annotate(
            total_resolvidos=Count("id"),
            resolvidos_no_prazo=Sum("_cumprido_sla"),
            media_satisfacao=Avg("avaliacao__nota"),
            total_avaliacoes=Count("avaliacao"),
            _satisfeitos=Count("id", filter=Q(avaliacao__nota__gte=4)),
        )
        .order_by("-total_resolvidos")
    )

    matriz: list[dict[str, Any]] = []
    for row in grouped:
        total = int(row["total_resolvidos"] or 0)
        if total <= 0:
            continue

        no_prazo = int(row["resolvidos_no_prazo"] or 0)
        taxa_sla = round(100.0 * no_prazo / total, 2)

        media_raw = row["media_satisfacao"]
        media = round(float(media_raw), 1) if media_raw is not None else None
        tot_av = int(row["total_avaliacoes"] or 0)
        satisfeitos = int(row["_satisfeitos"] or 0)
        pct_satisfeitos = (
            round(100.0 * satisfeitos / tot_av, 1) if tot_av > 0 else None
        )

        uid = row["servico__unidade_responsavel_id"]
        if uid is None:
            unidade_id = SEM_UNIDADE_ID
            nome = "Sem secretaria vinculada"
            sigla = "—"
            sem_vinculo = True
        else:
            unidade_id = str(uid)
            nome = row["servico__unidade_responsavel__nome"] or ""
            sigla = (row["servico__unidade_responsavel__sigla"] or "").strip()
            sem_vinculo = False

        matriz.append(
            {
                "unidade_id": unidade_id,
                "nome": nome,
                "sigla": sigla,
                "taxa_sla_cumprido": taxa_sla,
                "media_satisfacao": media,
                "total_avaliacoes": tot_av,
                "percentual_satisfeitos": pct_satisfeitos,
                "total_resolvidos": total,
                "resolvidos_no_prazo": no_prazo,
                "sem_vinculo_catalogo": sem_vinculo,
            }
        )

    matriz.sort(
        key=lambda x: (
            -(x["taxa_sla_cumprido"] or 0),
            -(x["media_satisfacao"] or 0),
        )
    )
    return matriz


def dashboard_qualidade(user, query_params=None) -> dict[str, Any]:
    """Matriz executiva SLA × satisfação por secretaria (escopo RBAC)."""
    escopo = escopo_dashboard(user)
    params = _query_params_dict(query_params)
    qs = queryset_protocolos_escopo(user)

    req_unidade = (params.get("unidade_responsavel_id") or "").strip() or None
    if escopo["tipo"] == "unidade" and escopo["unidade_id"]:
        if req_unidade and str(req_unidade) != str(escopo["unidade_id"]):
            raise PermissionDenied(
                "Consulta restrita à sua unidade administrativa."
            )
    elif req_unidade:
        qs = qs.filter(
            Q(servico__unidade_responsavel_id=req_unidade)
            | Q(ordens_servico__unidade_id=req_unidade)
        ).distinct()

    qs, bairro = aplicar_filtro_bairro(qs, params.get("bairro"))

    filtros_aplicados: dict[str, Any] = {}
    if bairro:
        filtros_aplicados["bairro"] = bairro
    if req_unidade:
        filtros_aplicados["unidade_responsavel_id"] = req_unidade

    matriz = calcular_matriz_qualidade_unidades(qs)

    tot_resolvidos = sum(u["total_resolvidos"] for u in matriz)
    tot_no_prazo = sum(u["resolvidos_no_prazo"] for u in matriz)
    taxa_geral = (
        round(100.0 * tot_no_prazo / tot_resolvidos, 2) if tot_resolvidos else 0.0
    )
    resumo_csat = calcular_resumo_csat(qs)

    return {
        "escopo": escopo["tipo"],
        "unidade_id": str(escopo["unidade_id"]) if escopo["unidade_id"] else None,
        "gerado_em": timezone.now().isoformat(),
        "filtros_aplicados": filtros_aplicados,
        "matriz_unidades": matriz,
        "resumo_geral": {
            "total_resolvidos": tot_resolvidos,
            "taxa_sla_cumprido": taxa_geral,
            **resumo_csat,
        },
    }