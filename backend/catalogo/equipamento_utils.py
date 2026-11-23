"""Busca e normalização de equipamentos públicos (PWA / slot filling)."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models import Case, IntegerField, Q, Value, When

from catalogo.datasources import LOOKUP_DATASOURCE_EQUIPAMENTOS
from catalogo.models import EquipamentoPublico


class CoordenadasInvalidasError(ValueError):
    """Par lat/lng inválido ou incompleto."""


def validar_faixa_coordenadas(latitude: float, longitude: float) -> None:
    if not (-90.0 <= latitude <= 90.0):
        raise CoordenadasInvalidasError("Latitude deve estar entre -90 e 90.")
    if not (-180.0 <= longitude <= 180.0):
        raise CoordenadasInvalidasError("Longitude deve estar entre -180 e 180.")


def ponto_wgs84(latitude: float, longitude: float) -> Point:
    validar_faixa_coordenadas(latitude, longitude)
    return Point(float(longitude), float(latitude), srid=4326)


def extrair_lat_lng(geometria) -> tuple[float | None, float | None]:
    if not geometria:
        return None, None
    return float(geometria.y), float(geometria.x)


def parse_lat_lng_query(
    lat_raw,
    lng_raw,
    *,
    exigir_par: bool = True,
) -> tuple[float | None, float | None, Point | None]:
    """
    Interpreta query ``lat``/``lng``.

    Se ``exigir_par`` e apenas um vier preenchido → CoordenadasInvalidasError.
    Se ambos ausentes → (None, None, None).
    """
    lat_vazio = lat_raw is None or str(lat_raw).strip() == ""
    lng_vazio = lng_raw is None or str(lng_raw).strip() == ""
    if lat_vazio and lng_vazio:
        return None, None, None
    if lat_vazio != lng_vazio:
        raise CoordenadasInvalidasError("Informe latitude e longitude juntos.")
    try:
        lat = float(str(lat_raw).strip().replace(",", "."))
        lng = float(str(lng_raw).strip().replace(",", "."))
    except (TypeError, ValueError) as exc:
        raise CoordenadasInvalidasError("Latitude e longitude devem ser numéricas.") from exc
    validar_faixa_coordenadas(lat, lng)
    return lat, lng, ponto_wgs84(lat, lng)


def serializar_equipamento_lookup_item(
    equipamento: EquipamentoPublico,
    *,
    distancia_metros: int | None = None,
    incluir_distancia: bool = False,
) -> dict:
    lat, lng = extrair_lat_lng(equipamento.localizacao)
    item = {
        "id": str(equipamento.id),
        "nome": equipamento.nome,
        "tipo": equipamento.tipo,
        "bairro": equipamento.bairro or "",
        "unidade_id": str(equipamento.unidade_responsavel_id),
        "unidade_nome": equipamento.unidade_responsavel.nome,
        "latitude": lat,
        "longitude": lng,
    }
    if incluir_distancia:
        item["distancia_metros"] = distancia_metros
    return item


def queryset_equipamentos_por_proximidade(qs, ref: Point):
    """Ordena por distância; itens sem geometria ficam ao final."""
    return (
        qs.annotate(distancia=Distance("localizacao", ref))
        .annotate(
            _sem_geo=Case(
                When(localizacao__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )
        .order_by("_sem_geo", "distancia", "nome")
    )


def distancia_em_metros(valor) -> int | None:
    if valor is None:
        return None
    try:
        return int(round(float(valor.m)))
    except (AttributeError, TypeError, ValueError):
        try:
            return int(round(float(valor)))
        except (TypeError, ValueError):
            return None


def normalizar_texto_busca(texto: str) -> str:
    s = unicodedata.normalize("NFD", (texto or "").strip())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE)
    s = re.sub(r"\s+", " ", s).strip()
    return s.casefold()


_STOPWORDS_EQUIPAMENTO = frozenset(
    {
        "de",
        "da",
        "do",
        "das",
        "dos",
        "em",
        "na",
        "no",
        "nas",
        "nos",
        "a",
        "o",
        "e",
        "as",
        "os",
    }
)


def tokens_significativos(texto: str) -> list[str]:
    """Tokens normalizados sem artigos/preposições (matching tolerante no chat)."""
    norm = normalizar_texto_busca(texto)
    brutos = re.findall(r"[a-z0-9]+", norm)
    return [t for t in brutos if t not in _STOPWORDS_EQUIPAMENTO and len(t) >= 2]


def termo_casa_no_texto(termo: str, texto: str) -> bool:
    """True se todos os tokens significativos do termo aparecem no texto."""
    tokens_termo = tokens_significativos(termo)
    if not tokens_termo:
        return False
    if sum(len(t) for t in tokens_termo) < 4:
        return False
    tokens_texto = set(tokens_significativos(texto))
    return all(t in tokens_texto for t in tokens_termo)


def _parse_datasource_filter(prop: dict | None) -> dict[str, Any]:
    raw = (prop or {}).get("x-ouvia-datasource-filter") or {}
    return raw if isinstance(raw, dict) else {}


def queryset_equipamentos_ativos(*, unidade_id=None, tipo=None):
    qs = (
        EquipamentoPublico.objects.filter(
            ativo=True,
            unidade_responsavel__ativo=True,
        )
        .select_related("unidade_responsavel")
        .order_by("nome")
    )
    if unidade_id:
        qs = qs.filter(unidade_responsavel_id=unidade_id)
    if tipo:
        qs = qs.filter(tipo=str(tipo).strip())
    return qs


def _coincide_texto(haystack: str, needle: str) -> bool:
    if not needle or not haystack:
        return False
    return normalizar_texto_busca(needle) in normalizar_texto_busca(haystack)


def equipamento_coincide_busca(equipamento: EquipamentoPublico, busca: str) -> bool:
    termo = (busca or "").strip()
    if not termo:
        return True
    if _coincide_texto(equipamento.nome, termo):
        return True
    if equipamento.bairro and _coincide_texto(equipamento.bairro, termo):
        return True
    for alias in equipamento.apelidos or []:
        if isinstance(alias, str) and _coincide_texto(alias, termo):
            return True
    return False


def filtrar_equipamentos_busca(qs, busca: str):
    termo = (busca or "").strip()
    if not termo:
        return qs
    base = qs.filter(Q(nome__icontains=termo) | Q(bairro__icontains=termo))
    ids_base = set(base.values_list("pk", flat=True))
    extra_ids: list[Any] = []
    for eq in qs.exclude(pk__in=ids_base).only("id", "nome", "bairro", "apelidos"):
        if equipamento_coincide_busca(eq, termo):
            extra_ids.append(eq.pk)
    if extra_ids:
        return qs.filter(Q(pk__in=ids_base) | Q(pk__in=extra_ids)).distinct()
    return base.distinct()


def campos_schema_datasource(schema: dict | None, datasource: str) -> list[str]:
    props = (schema or {}).get("properties") or {}
    if not isinstance(props, dict):
        return []
    chaves: list[str] = []
    for nome, prop in props.items():
        if not isinstance(prop, dict):
            continue
        ds = (prop.get("x-ouvia-datasource") or "").strip()
        if ds == datasource:
            chaves.append(str(nome))
    return chaves


def campos_equipamentos_publicos_schema(schema: dict | None) -> list[str]:
    return campos_schema_datasource(schema, LOOKUP_DATASOURCE_EQUIPAMENTOS)


def texto_contem_equipamento(texto: str, equipamento: EquipamentoPublico) -> bool:
    termos = [equipamento.nome] + [
        str(a).strip() for a in (equipamento.apelidos or []) if str(a).strip()
    ]
    for termo in termos:
        if termo_casa_no_texto(termo, texto):
            return True
        if len(normalizar_texto_busca(termo)) >= 4 and _coincide_texto(texto, termo):
            return True
    return False


def buscar_equipamentos_unicos_no_texto(
    texto: str,
    *,
    unidade_id=None,
    tipo=None,
) -> list[EquipamentoPublico]:
    qs = queryset_equipamentos_ativos(unidade_id=unidade_id, tipo=tipo)
    encontrados: list[EquipamentoPublico] = []
    for eq in qs:
        if texto_contem_equipamento(texto, eq):
            encontrados.append(eq)
    return encontrados