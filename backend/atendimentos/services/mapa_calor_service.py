"""Pontos geográficos para heatmap executivo (Leaflet) — consultas leves."""

from __future__ import annotations

from datetime import datetime, time
from typing import Any

from django.contrib.gis.db.models.fields import GeometryField
from django.core.exceptions import PermissionDenied
from django.db.models import Count, FloatField, Func, Q
from django.db.models.functions import Cast, Round
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from atendimentos.backoffice_serializers import calcular_sla
from atendimentos.models import Protocolo
from atendimentos.services.analytics_service import escopo_dashboard, queryset_protocolos_escopo
from atendimentos.services.dashboard_filters import aplicar_filtro_bairro
from atendimentos.services.protocolo_localidade import bairro_protocolo

MAPA_CALOR_LIMITE_PADRAO = 5000
COORD_CASAS_DECIMAIS = 4


class ST_Y(Func):
    function = "ST_Y"
    output_field = FloatField()


class ST_X(Func):
    function = "ST_X"
    output_field = FloatField()


def _parse_data_inicio(valor: str | None) -> datetime | None:
    if not valor:
        return None
    valor = valor.strip()
    dt = parse_datetime(valor)
    if dt:
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt
    d = parse_date(valor)
    if d:
        return timezone.make_aware(datetime.combine(d, time.min), timezone.get_current_timezone())
    return None


def _parse_data_fim(valor: str | None) -> datetime | None:
    if not valor:
        return None
    valor = valor.strip()
    dt = parse_datetime(valor)
    if dt:
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt
    d = parse_date(valor)
    if d:
        fim = datetime.combine(d, time.max)
        return timezone.make_aware(fim, timezone.get_current_timezone())
    return None


def _parse_status_list(valor: str | None) -> list[str]:
    if not valor:
        return []
    valid = {c[0] for c in Protocolo.Status.choices}
    out = []
    for parte in valor.split(","):
        s = parte.strip().lower()
        if s and s in valid:
            out.append(s)
    return out


def _geometria_wgs84():
    return Cast("localizacao", output_field=GeometryField(srid=4326))


def queryset_mapa_calor(user, query_params: dict) -> tuple[Any, dict[str, Any]]:
    """
    Aplica RBAC + filtros macro. Retorna queryset apenas com geo preenchido.
    """
    escopo = escopo_dashboard(user)
    meta: dict[str, Any] = {"escopo": escopo["tipo"]}

    qs = queryset_protocolos_escopo(user).filter(localizacao__isnull=False)

    req_unidade = (query_params.get("unidade_responsavel_id") or "").strip() or None
    if escopo["tipo"] == "unidade" and escopo["unidade_id"]:
        if req_unidade and str(req_unidade) != str(escopo["unidade_id"]):
            raise PermissionDenied(
                "Consulta restrita à sua unidade administrativa."
            )
        meta["unidade_id"] = str(escopo["unidade_id"])
    elif req_unidade:
        qs = qs.filter(
            Q(servico__unidade_responsavel_id=req_unidade)
            | Q(ordens_servico__unidade_id=req_unidade)
        ).distinct()
        meta["unidade_responsavel_id"] = req_unidade

    data_inicio = _parse_data_inicio(query_params.get("data_inicio"))
    data_fim = _parse_data_fim(query_params.get("data_fim"))
    if data_inicio:
        qs = qs.filter(data_criacao__gte=data_inicio)
        meta["data_inicio"] = data_inicio.isoformat()
    if data_fim:
        qs = qs.filter(data_criacao__lte=data_fim)
        meta["data_fim"] = data_fim.isoformat()

    servico_id = (query_params.get("servico_id") or "").strip() or None
    if servico_id:
        qs = qs.filter(servico_id=servico_id)
        meta["servico_id"] = servico_id

    categoria_id = (query_params.get("categoria_id") or "").strip() or None
    if categoria_id:
        qs = qs.filter(servico__categoria_id=categoria_id)
        meta["categoria_id"] = categoria_id

    status_list = _parse_status_list(query_params.get("status"))
    if status_list:
        qs = qs.filter(status__in=status_list)
        meta["status"] = status_list

    qs, bairro = aplicar_filtro_bairro(qs, query_params.get("bairro"))
    if bairro:
        meta["bairro"] = bairro

    return qs, meta


DESC_RESUMO_MAX = 280


def _incluir_demandas(query_params: dict) -> bool:
    bruto = (query_params.get("incluir_demandas") or "1").strip().lower()
    return bruto not in ("0", "false", "no")


def _nome_cidadao(usuario) -> str:
    if not usuario:
        return ""
    nome = (usuario.get_full_name() or "").strip()
    if nome:
        return nome
    return (getattr(usuario, "email", None) or "Cidadão").strip()


def _serializar_demanda_mapa(protocolo: Protocolo, lat: float, lng: float) -> dict[str, Any]:
    endereco_usuario = ""
    if protocolo.usuario_id:
        endereco = getattr(protocolo.usuario, "endereco", None)
        if endereco:
            endereco_usuario = (endereco.bairro or "").strip()

    bairro = bairro_protocolo(
        protocolo.dados_dinamicos,
        protocolo.endereco_texto or "",
        endereco_usuario,
    )
    descricao = (protocolo.descricao or "").strip()
    if len(descricao) > DESC_RESUMO_MAX:
        descricao = descricao[: DESC_RESUMO_MAX - 1].rstrip() + "…"

    sla = calcular_sla(protocolo)
    servico = protocolo.servico

    return {
        "id": str(protocolo.id),
        "codigo": protocolo.codigo,
        "status": protocolo.status,
        "descricao_resumo": descricao,
        "endereco": (protocolo.endereco_texto or "").strip(),
        "bairro": bairro,
        "latitude": lat,
        "longitude": lng,
        "data_criacao": protocolo.data_criacao.isoformat() if protocolo.data_criacao else None,
        "cidadao": {"nome": _nome_cidadao(protocolo.usuario)},
        "servico": {
            "id": str(servico.id) if servico else None,
            "nome": servico.nome if servico else "",
        },
        "sla": {
            "sla_horas": sla.get("sla_horas"),
            "vencido": bool(sla.get("vencido")),
            "horas_restantes": sla.get("horas_restantes"),
            "prazo_em": sla.get("prazo_em"),
        },
    }


def _limite_pontos(query_params: dict) -> int:
    bruto = query_params.get("limite")
    if bruto is None:
        return MAPA_CALOR_LIMITE_PADRAO
    try:
        n = int(bruto)
    except (TypeError, ValueError):
        return MAPA_CALOR_LIMITE_PADRAO
    return max(1, min(n, MAPA_CALOR_LIMITE_PADRAO))


def mapa_calor_pontos(user, query_params: dict) -> dict[str, Any]:
    """
    Extrai coordenadas [lat, lng] via ST_Y/ST_X no PostGIS (campo ``localizacao``).
    """
    qs, filtros = queryset_mapa_calor(user, query_params)
    total = qs.count()
    limite = _limite_pontos(query_params)
    agregar_pesos = str(query_params.get("agregar_pesos", "")).lower() in (
        "1",
        "true",
        "yes",
    )

    geom = _geometria_wgs84()
    qs = qs.annotate(_lat=ST_Y(geom), _lng=ST_X(geom))

    pontos: list[list[float]] = []
    pontos_ponderados: list[list[float]] = []
    demandas: list[dict[str, Any]] = []
    incluir_demandas = _incluir_demandas(query_params)

    if agregar_pesos:
        agregados = (
            qs.annotate(
                lat_r=Round("_lat", COORD_CASAS_DECIMAIS),
                lng_r=Round("_lng", COORD_CASAS_DECIMAIS),
            )
            .values("lat_r", "lng_r")
            .annotate(peso=Count("id"))
            .order_by("-peso")[:limite]
        )
        for row in agregados:
            if row["lat_r"] is None or row["lng_r"] is None:
                continue
            lat = float(row["lat_r"])
            lng = float(row["lng_r"])
            peso = float(row["peso"] or 1)
            pontos.append([lat, lng])
            pontos_ponderados.append([lat, lng, peso])
        truncado = total > len(pontos) and len(pontos) >= limite
    else:
        if incluir_demandas:
            protocolos = list(
                qs.select_related("servico", "usuario", "usuario__endereco")
                .order_by("-data_criacao")[:limite]
            )
            for proto in protocolos:
                if proto._lat is None or proto._lng is None:
                    continue
                lat = float(proto._lat)
                lng = float(proto._lng)
                pontos.append([lat, lng])
                demandas.append(_serializar_demanda_mapa(proto, lat, lng))
            truncado = total > len(pontos)
        else:
            rows = list(
                qs.order_by("-data_criacao").values_list("_lat", "_lng")[:limite]
            )
            pontos = [
                [float(lat), float(lng)]
                for lat, lng in rows
                if lat is not None and lng is not None
            ]
            truncado = total > len(pontos)

    payload: dict[str, Any] = {
        "gerado_em": timezone.now().isoformat(),
        "filtros_aplicados": filtros,
        "pontos": pontos,
        "total": total,
        "retornados": len(pontos),
        "limite": limite,
        "truncado": truncado,
    }
    if agregar_pesos:
        payload["pontos_ponderados"] = pontos_ponderados
    if incluir_demandas and not agregar_pesos:
        payload["demandas"] = demandas
    return payload