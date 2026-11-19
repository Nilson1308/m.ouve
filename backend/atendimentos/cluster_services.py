"""Motor de clusterização geográfica para sugestões de Super OS."""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import timedelta
from typing import Any

from django.db.models import QuerySet
from django.utils import timezone

from django.db.models import Prefetch

from atendimentos.models import ConfiguracaoSistema, OrdemServico, Protocolo, SuperOS

EARTH_RADIUS_M = 6_371_000
DEFAULT_RAIO_METROS = 300

# Equipe ainda pode agir em campo / mesa — protocolos e Super OS elegíveis ao agrupamento.
STATUS_AGRUPAVEL_IA = frozenset(
    {
        Protocolo.Status.EM_ANALISE,
        Protocolo.Status.EM_ANDAMENTO,
    }
)

# Serviço de campo considerado concluído ou em encerramento — excluir da IA.
STATUS_EXCLUIDO_CLUSTER_IA = frozenset(
    {
        Protocolo.Status.AGUARDANDO_REVISAO,
        Protocolo.Status.RESOLVIDO,
        Protocolo.Status.REJEITADO,
    }
)

TIPO_ACAO_CRIAR = "criar"
TIPO_ACAO_ANEXAR = "anexar"
TIPO_ACAO_CRIAR_RETROATIVA = "criar_retroativa"

OS_ENCERRADA = frozenset(
    {
        OrdemServico.Status.CONCLUIDA,
        OrdemServico.Status.CANCELADA,
    }
)

OS_ATIVA_CAMP = frozenset(
    {
        OrdemServico.Status.PENDENTE,
        OrdemServico.Status.EM_ANDAMENTO,
        OrdemServico.Status.AGUARDANDO_FORMALIZACAO,
        OrdemServico.Status.AGUARDANDO_ASSINATURA,
    }
)


def haversine_metros(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distância em metros entre duas coordenadas (WGS84)."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def dias_janela_cluster_ia() -> int:
    cfg = ConfiguracaoSistema.load()
    return max(1, min(int(cfg.dias_busca_cluster_ia), 365))


def _coords_protocolo(protocolo: Protocolo) -> tuple[float, float] | None:
    if not protocolo.localizacao:
        return None
    return float(protocolo.localizacao.y), float(protocolo.localizacao.x)


def _coords_super_os(super_os: SuperOS) -> tuple[float, float] | None:
    if super_os.latitude_centro is not None and super_os.longitude_centro is not None:
        return float(super_os.latitude_centro), float(super_os.longitude_centro)
    filhos = list(
        super_os.protocolos_filhos.filter(localizacao__isnull=False).order_by(
            "data_criacao"
        )[:30]
    )
    if not filhos:
        return None
    lat, lon = centroide(filhos)
    if lat is None or lon is None:
        return None
    return lat, lon


def _prefetch_ordens_ativas():
    return Prefetch(
        "ordens_servico",
        queryset=OrdemServico.objects.exclude(status__in=OS_ENCERRADA),
    )


def protocolo_elegivel_clusterizacao(protocolo: Protocolo) -> bool:
    """Respeita ``ServicoCatalogo.permite_cluster`` (defesa em profundidade)."""
    if not protocolo.servico_id:
        return False
    servico = protocolo.servico
    return bool(getattr(servico, "permite_cluster", True))


def queryset_candidatos_cluster() -> QuerySet[Protocolo]:
    """Protocolos abertos na janela temporal, com geo, ainda sem Super OS."""
    cutoff = timezone.now() - timedelta(days=dias_janela_cluster_ia())
    return (
        Protocolo.objects.filter(
            status__in=STATUS_AGRUPAVEL_IA,
            super_os__isnull=True,
            localizacao__isnull=False,
            servico__permite_cluster=True,
            data_criacao__gte=cutoff,
        )
        .select_related("servico", "super_os")
        .prefetch_related(_prefetch_ordens_ativas())
        .order_by("data_criacao")
    )


def protocolo_tem_os_ativa(protocolo: Protocolo) -> bool:
    cache = getattr(protocolo, "_prefetched_objects_cache", None)
    if cache and "ordens_servico" in cache:
        return any(o.status in OS_ATIVA_CAMP for o in protocolo.ordens_servico.all())
    return protocolo.ordens_servico.exclude(status__in=OS_ENCERRADA).filter(
        status__in=OS_ATIVA_CAMP
    ).exists()


def super_os_tem_os_ativa(super_os: SuperOS) -> bool:
    if hasattr(super_os, "_prefetched_ordens_ativas"):
        return bool(super_os._prefetched_ordens_ativas)
    return super_os.ordens_servico.exclude(status__in=OS_ENCERRADA).filter(
        status__in=OS_ATIVA_CAMP
    ).exists()


def _score_os_prioridade(protocolo: Protocolo) -> int:
    """Maior = mais avançado no campo (âncora preferida)."""
    pesos = {
        OrdemServico.Status.EM_ANDAMENTO: 80,
        OrdemServico.Status.AGUARDANDO_FORMALIZACAO: 70,
        OrdemServico.Status.AGUARDANDO_ASSINATURA: 60,
        OrdemServico.Status.PENDENTE: 40,
    }
    cache = getattr(protocolo, "_prefetched_objects_cache", None)
    ordens = (
        protocolo.ordens_servico.all()
        if cache and "ordens_servico" in cache
        else protocolo.ordens_servico.exclude(status__in=OS_ENCERRADA)
    )
    melhor = 0
    for o in ordens:
        if o.status in OS_ATIVA_CAMP:
            melhor = max(melhor, pesos.get(o.status, 30))
    return melhor


def escolher_ancora_cluster(grupo: list[Protocolo]) -> dict[str, Any] | None:
    """
    Define o nó mais avançado do cluster (Super OS com OS ativa ou protocolo despachado).
    """
    melhor: dict[str, Any] | None = None
    melhor_score = -1

    for p in grupo:
        if p.super_os_id:
            sos = p.super_os
            if sos and super_os_tem_os_ativa(sos):
                score = 200 + sos.protocolos_filhos.count()
                if score > melhor_score:
                    melhor_score = score
                    melhor = {"tipo": "super_os", "super_os": sos, "protocolo": p}

        if not p.super_os_id and protocolo_tem_os_ativa(p):
            score = 100 + _score_os_prioridade(p)
            if score > melhor_score:
                melhor_score = score
                melhor = {"tipo": "protocolo", "super_os": None, "protocolo": p}

    return melhor


def queryset_super_os_agrupaveis() -> QuerySet[SuperOS]:
    """Super OS onde ainda faz sentido anexar novos relatos (equipe em atividade)."""
    return (
        SuperOS.objects.filter(status__in=STATUS_AGRUPAVEL_IA)
        .prefetch_related(
            "protocolos_filhos",
            Prefetch(
                "ordens_servico",
                queryset=OrdemServico.objects.exclude(status__in=OS_ENCERRADA),
            ),
        )
        .order_by("-criado_em")
    )


def _referencia_local(protocolo: Protocolo) -> str:
    if (protocolo.endereco_texto or "").strip():
        ref = protocolo.endereco_texto.strip()
        return ref if len(ref) <= 80 else ref[:77] + "…"
    dados = protocolo.dados_dinamicos or {}
    bairro = (dados.get("bairro") or "").strip()
    if bairro:
        return bairro
    return "área indicada"


class _UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def clusterizar_por_servico_e_raio(
    protocolos: list[Protocolo],
    raio_metros: float = DEFAULT_RAIO_METROS,
) -> list[list[Protocolo]]:
    """Agrupa protocolos do mesmo serviço dentro do raio (componentes conexas)."""
    por_servico: dict[Any, list[tuple[Protocolo, float, float]]] = defaultdict(list)
    for p in protocolos:
        if not protocolo_elegivel_clusterizacao(p):
            continue
        coords = _coords_protocolo(p)
        if coords is None:
            continue
        por_servico[p.servico_id].append((p, coords[0], coords[1]))

    clusters: list[list[Protocolo]] = []
    for items in por_servico.values():
        n = len(items)
        if n < 2:
            continue
        uf = _UnionFind(n)
        for i in range(n):
            for j in range(i + 1, n):
                _, lat_i, lon_i = items[i]
                _, lat_j, lon_j = items[j]
                if haversine_metros(lat_i, lon_i, lat_j, lon_j) <= raio_metros:
                    uf.union(i, j)
        grupos: dict[int, list[Protocolo]] = defaultdict(list)
        for idx, (proto, _, _) in enumerate(items):
            grupos[uf.find(idx)].append(proto)
        for grupo in grupos.values():
            if len(grupo) >= 2:
                clusters.append(grupo)
    return clusters


def titulo_sugestao_cluster(protocolos: list[Protocolo]) -> str:
    qtd = len(protocolos)
    servico_nome = protocolos[0].servico.nome if protocolos[0].servico_id else "Serviço"
    ref = _referencia_local(protocolos[0])
    return f"{qtd} protocolos de {servico_nome} próximos à {ref}"


def titulo_sugestao_retroativa(ancora: Protocolo, protocolos: list[Protocolo]) -> str:
    qtd = len(protocolos)
    servico_nome = ancora.servico.nome if ancora.servico_id else "Serviço"
    return (
        f"Agrupar {qtd} protocolo(s) à âncora operacional {ancora.codigo} "
        f"({servico_nome}) — incidente já no Painel Setorial"
    )


def titulo_sugestao_anexar(super_os: SuperOS, protocolos: list[Protocolo]) -> str:
    qtd = len(protocolos)
    servico_nome = (
        protocolos[0].servico.nome if protocolos and protocolos[0].servico_id else "Serviço"
    )
    return (
        f"Anexar {qtd} protocolo(s) de {servico_nome} à Super OS "
        f"{super_os.codigo} — {super_os.titulo_resumo}"
    )


def centroide(protocolos: list[Protocolo]) -> tuple[float | None, float | None]:
    lats: list[float] = []
    lons: list[float] = []
    for p in protocolos:
        c = _coords_protocolo(p)
        if c:
            lats.append(c[0])
            lons.append(c[1])
    if not lats:
        return None, None
    return sum(lats) / len(lats), sum(lons) / len(lons)


def _servico_ids_super_os(super_os: SuperOS) -> set:
    return {
        sid for sid in super_os.protocolos_filhos.values_list("servico_id", flat=True) if sid
    }


def _super_os_aceita_servico(super_os: SuperOS, servico_id) -> bool:
    ids = _servico_ids_super_os(super_os)
    if not ids:
        return True
    return servico_id in ids


def gerar_sugestoes_anexar(
    candidatos: list[Protocolo],
    super_os_list: list[SuperOS],
    raio_metros: float,
) -> tuple[list[dict[str, Any]], set[Any]]:
    """Vincula protocolos a Super OS existentes próximas; retorna sugestões e IDs reservados."""
    if not candidatos or not super_os_list:
        return [], set()

    super_index: list[tuple[SuperOS, float, float, set]] = []
    for sos in super_os_list:
        coords = _coords_super_os(sos)
        if coords is None:
            continue
        sos._prefetched_ordens_ativas = list(
            o
            for o in sos.ordens_servico.all()
            if o.status not in OS_ENCERRADA and o.status in OS_ATIVA_CAMP
        )
        super_index.append((sos, coords[0], coords[1], _servico_ids_super_os(sos)))

    por_super: dict[Any, list[Protocolo]] = defaultdict(list)
    reserved: set[Any] = set()

    for protocolo in candidatos:
        if not protocolo_elegivel_clusterizacao(protocolo):
            continue
        pc = _coords_protocolo(protocolo)
        if pc is None or not protocolo.servico_id:
            continue
        melhor: tuple[SuperOS, float] | None = None
        for sos, lat, lon, servicos in super_index:
            if servicos and protocolo.servico_id not in servicos:
                continue
            dist = haversine_metros(pc[0], pc[1], lat, lon)
            if dist <= raio_metros:
                score_dist = dist
                if super_os_tem_os_ativa(sos):
                    score_dist -= 50.0
                if melhor is None or score_dist < melhor[1]:
                    melhor = (sos, score_dist)
        if melhor:
            por_super[melhor[0].id].append(protocolo)

    sugestoes: list[dict[str, Any]] = []
    for sos_id, grupo in por_super.items():
        if not grupo:
            continue
        sos = next(s for s, *_ in super_index if s.id == sos_id)
        lat, lon = centroide(grupo)
        reserved.update(p.id for p in grupo)
        sugestoes.append(
            {
                "tipo_acao": TIPO_ACAO_ANEXAR,
                "titulo": titulo_sugestao_anexar(sos, grupo),
                "super_os_id": str(sos.id),
                "super_os_codigo": sos.codigo,
                "super_os_titulo": sos.titulo_resumo,
                "servico_id": str(grupo[0].servico_id),
                "servico_nome": grupo[0].servico.nome if grupo[0].servico_id else "",
                "protocolo_ids": [str(p.id) for p in grupo],
                "quantidade": len(grupo),
                "latitude_centro": lat,
                "longitude_centro": lon,
                "raio_metros": raio_metros,
            }
        )
    return sugestoes, reserved


def gerar_sugestoes_retroativa_por_ancora(
    candidatos: list[Protocolo],
    raio_metros: float,
    reservados: set[Any],
) -> tuple[list[dict[str, Any]], set[Any]]:
    """Protocolos já despachados (âncora) + vizinhos elegíveis — fora do cluster ≥ min."""
    ancoras = [
        p
        for p in candidatos
        if p.id not in reservados
        and not p.super_os_id
        and protocolo_tem_os_ativa(p)
        and protocolo_elegivel_clusterizacao(p)
    ]
    if not ancoras:
        return [], reservados

    extra_reserved = set(reservados)
    sugestoes: list[dict[str, Any]] = []

    for ancora in ancoras:
        ac = _coords_protocolo(ancora)
        if not ac or not ancora.servico_id:
            continue
        vizinhos: list[Protocolo] = []
        for protocolo in candidatos:
            if protocolo.id in extra_reserved or protocolo.id == ancora.id:
                continue
            if not protocolo_elegivel_clusterizacao(protocolo):
                continue
            if protocolo.super_os_id or protocolo_tem_os_ativa(protocolo):
                continue
            if protocolo.servico_id != ancora.servico_id:
                continue
            pc = _coords_protocolo(protocolo)
            if not pc:
                continue
            if haversine_metros(ac[0], ac[1], pc[0], pc[1]) <= raio_metros:
                vizinhos.append(protocolo)
        if not vizinhos:
            continue
        lat, lon = centroide([ancora, *vizinhos])
        sugestoes.append(
            {
                "tipo_acao": TIPO_ACAO_CRIAR_RETROATIVA,
                "titulo": titulo_sugestao_retroativa(ancora, vizinhos),
                "protocolo_ancora_id": str(ancora.id),
                "protocolo_ancora_codigo": ancora.codigo,
                "servico_id": str(ancora.servico_id),
                "servico_nome": ancora.servico.nome if ancora.servico_id else "",
                "protocolo_ids": [str(p.id) for p in vizinhos],
                "protocolos_envolvidos_ids": [str(ancora.id)] + [str(p.id) for p in vizinhos],
                "quantidade": len(vizinhos),
                "latitude_centro": lat,
                "longitude_centro": lon,
                "raio_metros": raio_metros,
            }
        )
        extra_reserved.add(ancora.id)
        extra_reserved.update(p.id for p in vizinhos)

    return sugestoes, extra_reserved


def gerar_sugestoes_super_os(
    raio_metros: float = DEFAULT_RAIO_METROS,
    min_protocolos: int = 2,
) -> list[dict[str, Any]]:
    candidatos = list(queryset_candidatos_cluster())
    super_os_list = list(queryset_super_os_agrupaveis())

    sugestoes_anexar, reservados = gerar_sugestoes_anexar(
        candidatos, super_os_list, raio_metros=raio_metros
    )
    sugestoes_retroativa_solta, reservados = gerar_sugestoes_retroativa_por_ancora(
        candidatos, raio_metros=raio_metros, reservados=reservados
    )
    restantes = [p for p in candidatos if p.id not in reservados]

    clusters = clusterizar_por_servico_e_raio(restantes, raio_metros=raio_metros)
    sugestoes_criar: list[dict[str, Any]] = []
    sugestoes_retroativa: list[dict[str, Any]] = []

    for grupo in clusters:
        if len(grupo) < min_protocolos:
            continue

        ancora_info = escolher_ancora_cluster(grupo)
        lat, lon = centroide(grupo)

        if ancora_info and ancora_info["tipo"] == "super_os":
            sos = ancora_info["super_os"]
            novos = [p for p in grupo if not p.super_os_id]
            if novos:
                sugestoes_retroativa.append(
                    {
                        "tipo_acao": TIPO_ACAO_ANEXAR,
                        "titulo": titulo_sugestao_anexar(sos, novos),
                        "super_os_id": str(sos.id),
                        "super_os_codigo": sos.codigo,
                        "super_os_titulo": sos.titulo_resumo,
                        "servico_id": str(novos[0].servico_id) if novos[0].servico_id else "",
                        "servico_nome": (
                            novos[0].servico.nome if novos[0].servico_id else ""
                        ),
                        "protocolo_ids": [str(p.id) for p in novos],
                        "quantidade": len(novos),
                        "latitude_centro": lat,
                        "longitude_centro": lon,
                        "raio_metros": raio_metros,
                    }
                )
            continue

        if ancora_info and ancora_info["tipo"] == "protocolo":
            ancora = ancora_info["protocolo"]
            novos = [
                p
                for p in grupo
                if p.id != ancora.id and not p.super_os_id and not protocolo_tem_os_ativa(p)
            ]
            if not novos:
                continue
            sugestoes_retroativa.append(
                {
                    "tipo_acao": TIPO_ACAO_CRIAR_RETROATIVA,
                    "titulo": titulo_sugestao_retroativa(ancora, novos),
                    "protocolo_ancora_id": str(ancora.id),
                    "protocolo_ancora_codigo": ancora.codigo,
                    "servico_id": str(ancora.servico_id) if ancora.servico_id else "",
                    "servico_nome": ancora.servico.nome if ancora.servico_id else "",
                    "protocolo_ids": [str(p.id) for p in novos],
                    "protocolos_envolvidos_ids": [str(p.id) for p in grupo],
                    "quantidade": len(novos),
                    "latitude_centro": lat,
                    "longitude_centro": lon,
                    "raio_metros": raio_metros,
                }
            )
            continue

        if any(protocolo_tem_os_ativa(p) for p in grupo):
            continue

        sugestoes_criar.append(
            {
                "tipo_acao": TIPO_ACAO_CRIAR,
                "titulo": titulo_sugestao_cluster(grupo),
                "servico_id": str(grupo[0].servico_id),
                "servico_nome": grupo[0].servico.nome if grupo[0].servico_id else "",
                "protocolo_ids": [str(p.id) for p in grupo],
                "quantidade": len(grupo),
                "latitude_centro": lat,
                "longitude_centro": lon,
                "raio_metros": raio_metros,
            }
        )

    sugestoes = (
        sugestoes_anexar + sugestoes_retroativa_solta + sugestoes_retroativa + sugestoes_criar
    )
    sugestoes.sort(key=lambda s: (-s["quantidade"], s.get("tipo_acao", ""), s["titulo"]))
    return sugestoes