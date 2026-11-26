"""Montagem do Kanban unificado (protocolos isolados + Super OS)."""

from __future__ import annotations

from django.db.models import Count, Prefetch, Q
from django.utils import timezone

from atendimentos.backoffice_serializers import calcular_sla, extrair_urgencia
from atendimentos.models import OrdemServico, Protocolo, SuperOS
from atendimentos.services.escopo_dados import aplicar_escopo_protocolos
from atendimentos.super_os_services import super_os_precisa_integracao_ancora
from atendimentos.urgencia_constants import normalizar_nivel, peso_nivel


def _peso_urgencia(valor: str | None) -> int:
    return peso_nivel(normalizar_nivel(valor))


def _peso_urgencia_protocolo(protocolo: Protocolo) -> int:
    if getattr(protocolo, "urgencia_peso", None):
        return int(protocolo.urgencia_peso)
    return peso_nivel(extrair_urgencia(protocolo))


def _titulo_protocolo(protocolo: Protocolo) -> str:
    servico = protocolo.servico.nome if protocolo.servico_id else "Protocolo"
    return f"{servico} · {protocolo.codigo}"


def _prazo_operacional_horas(protocolo: Protocolo) -> int | None:
    ativa = (
        protocolo.ordens_servico.exclude(status=OrdemServico.Status.CANCELADA)
        .order_by("prazo_horas")
        .first()
    )
    if ativa and ativa.prazo_horas:
        return int(ativa.prazo_horas)
    if protocolo.servico_id:
        return int(protocolo.servico.sla_horas)
    return 72


def montar_item_protocolo(protocolo: Protocolo) -> dict:
    sla = calcular_sla(protocolo)
    urgencia = extrair_urgencia(protocolo)
    u = protocolo.usuario
    cidadao = (
        {
            "id": str(u.id),
            "nome": u.nome,
            "telefone": u.telefone or "",
        }
        if u
        else {"nome": "—", "telefone": ""}
    )
    equipamento_payload = None
    eq = getattr(protocolo, "equipamento", None)
    if eq:
        equipamento_payload = {
            "id": str(eq.id),
            "nome": eq.nome,
            "tipo": eq.tipo,
            "bairro": eq.bairro or "",
        }

    return {
        "id": str(protocolo.id),
        "tipo": "protocolo",
        "codigo": protocolo.codigo,
        "titulo": _titulo_protocolo(protocolo),
        "status": protocolo.status,
        "prazo_horas": _prazo_operacional_horas(protocolo),
        "urgencia": urgencia,
        "qtd_filhos": 0,
        "sla": sla,
        "criado_em": protocolo.data_criacao.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endereco": protocolo.endereco_texto or "",
        "servico_nome": protocolo.servico.nome if protocolo.servico_id else None,
        "cidadao": cidadao,
        "equipamento": equipamento_payload,
        "triagem_sugerida": protocolo.triagem_sugerida or {},
        "_sort_vencido": sla["vencido"],
        "_sort_horas": sla["horas_restantes"],
        "_sort_urgencia": _peso_urgencia_protocolo(protocolo),
        "_sort_criado": protocolo.data_criacao,
    }


def _agregar_sla_filhos(filhos: list[Protocolo]) -> dict:
    if not filhos:
        agora = timezone.now()
        return {
            "sla_horas": 72,
            "prazo_em": agora.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "vencido": False,
            "horas_restantes": 72.0,
        }
    slas = [calcular_sla(p) for p in filhos]
    vencido = any(s["vencido"] for s in slas)
    horas = min(s["horas_restantes"] for s in slas)
    pior = next(s for s in slas if s["vencido"] == vencido and s["horas_restantes"] == horas)
    return {
        "sla_horas": pior.get("sla_horas", 72),
        "prazo_em": pior["prazo_em"],
        "vencido": vencido,
        "horas_restantes": horas,
    }


def _agregar_urgencia_filhos(filhos: list[Protocolo]) -> str:
    melhor = "media"
    peso = 99
    for p in filhos:
        u = extrair_urgencia(p)
        pu = _peso_urgencia(u)
        if pu < peso:
            peso = pu
            melhor = u
    return melhor


def _prazo_super_os(super_os: SuperOS, filhos: list[Protocolo]) -> int | None:
    ordem = (
        super_os.ordens_servico.exclude(status=OrdemServico.Status.CANCELADA)
        .order_by("prazo_horas")
        .first()
    )
    if ordem and ordem.prazo_horas:
        return int(ordem.prazo_horas)
    if filhos and filhos[0].servico_id:
        return int(filhos[0].servico.sla_horas)
    return 72


def montar_item_super_os(super_os: SuperOS, filhos: list[Protocolo]) -> dict:
    qtd = getattr(super_os, "qtd_filhos", None)
    if qtd is None:
        qtd = len(filhos)
    sla = _agregar_sla_filhos(filhos)
    urgencia = _agregar_urgencia_filhos(filhos)
    precisa_integracao = super_os_precisa_integracao_ancora(super_os)
    return {
        "id": str(super_os.id),
        "tipo": "super_os",
        "codigo": super_os.codigo,
        "titulo": super_os.titulo_resumo,
        "status": super_os.status,
        "precisa_integracao_ancora": precisa_integracao,
        "prazo_horas": _prazo_super_os(super_os, filhos),
        "urgencia": urgencia,
        "qtd_filhos": qtd,
        "sla": sla,
        "criado_em": super_os.criado_em.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endereco": filhos[0].endereco_texto if filhos else "",
        "servico_nome": filhos[0].servico.nome if filhos and filhos[0].servico_id else None,
        "_sort_vencido": sla["vencido"],
        "_sort_horas": sla["horas_restantes"],
        "_sort_urgencia": _peso_urgencia(urgencia),
        "_sort_criado": super_os.criado_em,
    }


def ordenar_itens_kanban(itens: list[dict]) -> list[dict]:
    """Prioridade: maior urgência, depois SLA mais próximo de vencer."""

    def chave(item: dict):
        return (
            -item["_sort_urgencia"],
            0 if item["_sort_vencido"] else 1,
            item["_sort_horas"],
            item["_sort_criado"],
        )

    itens.sort(key=chave)
    for item in itens:
        item.pop("_sort_vencido", None)
        item.pop("_sort_horas", None)
        item.pop("_sort_urgencia", None)
        item.pop("_sort_criado", None)
    return itens


def queryset_protocolos_kanban(user=None):
    ordens_qs = OrdemServico.objects.select_related("unidade").order_by("criado_em")
    qs = (
        Protocolo.objects.filter(super_os__isnull=True)
        .select_related("servico", "servico__categoria", "usuario", "equipamento")
        .prefetch_related(Prefetch("ordens_servico", queryset=ordens_qs))
        .annotate(_tem_anexos=Count("anexos", distinct=True))
    )
    if user is not None:
        qs = aplicar_escopo_protocolos(user, qs)
    return qs


def queryset_super_os_kanban(user=None):
    filhos_qs = (
        Protocolo.objects.select_related("servico")
        .prefetch_related(
            Prefetch(
                "ordens_servico",
                queryset=OrdemServico.objects.exclude(
                    status=OrdemServico.Status.CANCELADA
                ),
            )
        )
        .order_by("data_criacao")
    )
    qs = (
        SuperOS.objects.annotate(qtd_filhos=Count("protocolos_filhos", distinct=True))
        .prefetch_related(Prefetch("protocolos_filhos", queryset=filhos_qs))
        .prefetch_related(
            Prefetch(
                "ordens_servico",
                queryset=OrdemServico.objects.exclude(status=OrdemServico.Status.CANCELADA),
            )
        )
    )
    if user is not None:
        visiveis = aplicar_escopo_protocolos(user, Protocolo.objects.all()).filter(
            super_os__isnull=False
        )
        qs = qs.filter(protocolos_filhos__in=visiveis).distinct()
    return qs


def _parametros_ativos(params) -> set[str]:
    """Chaves de filtro presentes na query (multi-value ou escalar)."""
    chaves = {
        "busca",
        "status",
        "sla_vencido",
        "urgencia",
        "unidade_id",
        "servico_id",
        "bairro",
        "equipamento_id",
        "apenas_cobrados",
        "apenas_reabertos",
        "apenas_sugestao_urgencia_ia",
    }
    ativos: set[str] = set()
    if hasattr(params, "keys"):
        for key in chaves:
            if hasattr(params, "getlist"):
                if params.getlist(key):
                    ativos.add(key)
                    continue
            raw = params.get(key)
            if raw not in (None, "", [], ()):
                ativos.add(key)
    elif isinstance(params, dict):
        for key in chaves:
            raw = params.get(key)
            if raw not in (None, "", [], ()):
                ativos.add(key)
    return ativos


def _filtros_so_super_os(params) -> bool:
    """True quando só busca/status afetam cartões de Super OS (sem recorte por filhos)."""
    ativos = _parametros_ativos(params)
    restritivos = ativos - {"busca", "status"}
    return not restritivos


def filtrar_protocolos_kanban(qs, params):
    """Mesma semântica de ``GET /backoffice/protocolos`` (matriz de urgência inclusa)."""
    from atendimentos.backoffice_views import BackofficeProtocoloFilterSet

    fs = BackofficeProtocoloFilterSet(params, queryset=qs)
    if not fs.is_valid():
        return qs
    return fs.qs.distinct()


def filtrar_super_os_kanban(qs, params):
    status = params.get("status")
    if status:
        valores = [v.strip() for v in status.split(",") if v.strip()]
        if valores:
            qs = qs.filter(status__in=valores)

    busca = (params.get("busca") or "").strip()
    if busca:
        qs = qs.filter(
            Q(codigo__icontains=busca)
            | Q(titulo_resumo__icontains=busca)
            | Q(descricao_geral__icontains=busca)
        )
    return qs


def resumo_contadores_mesa(itens: list[dict], *, user=None, params=None) -> dict:
    """Totais do recorte filtrado (todos os cartões, não só a página)."""
    resumo = {
        "total_itens": len(itens),
        "em_andamento": 0,
        "aguardando_validacao": 0,
        "sla_vencido": 0,
        "criticos": 0,
        "concluidos_hoje": 0,
    }
    for item in itens:
        status = (item.get("status") or "").lower()
        if status == Protocolo.Status.EM_ANDAMENTO:
            resumo["em_andamento"] += 1
        if status == Protocolo.Status.AGUARDANDO_REVISAO:
            resumo["aguardando_validacao"] += 1
        if (item.get("sla") or {}).get("vencido"):
            resumo["sla_vencido"] += 1
        if (item.get("urgencia") or "").lower() == Protocolo.Urgencia.CRITICA:
            resumo["criticos"] += 1
    if user is not None and params is not None:
        hoje = timezone.localdate()
        proto_qs = filtrar_protocolos_kanban(queryset_protocolos_kanban(user), params)
        resumo["concluidos_hoje"] = proto_qs.filter(
            status=Protocolo.Status.RESOLVIDO,
            data_atualizacao__date=hoje,
        ).count()
    return resumo


def montar_kanban_unificado(request_query_params, *, user=None) -> list[dict]:
    proto_base = queryset_protocolos_kanban(user)
    protocolos = list(filtrar_protocolos_kanban(proto_base, request_query_params))

    super_qs = filtrar_super_os_kanban(queryset_super_os_kanban(user), request_query_params)
    if _filtros_so_super_os(request_query_params):
        super_list = list(super_qs)
    else:
        filhos_qs = filtrar_protocolos_kanban(
            Protocolo.objects.filter(super_os__isnull=False),
            request_query_params,
        )
        ids_super = set(
            filhos_qs.exclude(super_os_id__isnull=True).values_list("super_os_id", flat=True)
        )
        super_list = list(super_qs.filter(pk__in=ids_super)) if ids_super else []

    itens = [montar_item_protocolo(p) for p in protocolos]
    for sos in super_list:
        filhos = list(sos.protocolos_filhos.all())
        itens.append(montar_item_super_os(sos, filhos))

    return ordenar_itens_kanban(itens)