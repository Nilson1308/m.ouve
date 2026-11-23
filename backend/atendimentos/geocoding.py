"""Geocodificação gratuita via Nominatim (OpenStreetMap)."""

import logging
import re

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

NOMINATIM_BASE = "https://nominatim.openstreetmap.org"
DEFAULT_TIMEOUT = 12
CEP_RE = re.compile(r"\b\d{5}-?\d{3}\b")
# Prioriza região metropolitana (Mogi e entorno) sem bloquear resultados distantes
VIEWBOX_REGIAO_PADRAO = "-46.38,-23.40,-46.02,-23.68"


def _headers():
    return {
        "User-Agent": getattr(
            settings,
            "NOMINATIM_USER_AGENT",
            "OuvIA/1.0 (municipal; contato@ouvia.local)",
        ),
        "Accept-Language": "pt-BR,pt;q=0.9",
    }


def reverse_geocode(latitude: float, longitude: float) -> dict | None:
    try:
        response = requests.get(
            f"{NOMINATIM_BASE}/reverse",
            params={
                "lat": latitude,
                "lon": longitude,
                "format": "json",
                "addressdetails": 1,
            },
            headers=_headers(),
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        logger.warning("Nominatim reverse falhou: %s", exc)
        return None

    address = data.get("address") or {}
    rua = address.get("road") or address.get("pedestrian") or ""
    numero = address.get("house_number") or ""
    bairro = (
        address.get("suburb")
        or address.get("neighbourhood")
        or address.get("quarter")
        or ""
    )
    cidade = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
        or ""
    )
    estado = address.get("state") or ""
    cep = address.get("postcode") or ""
    partes = [p for p in [rua, numero, bairro, cidade, estado] if p]
    endereco_completo = data.get("display_name") or ", ".join(partes)

    return {
        "endereco_completo": endereco_completo,
        "rua": rua,
        "numero": numero,
        "bairro": bairro,
        "cidade": cidade,
        "estado": estado,
        "cep": cep,
        "fonte": "nominatim",
    }


def _expand_search_queries(query: str) -> list[str]:
    texto = (query or "").strip()
    if not texto:
        return []
    variantes: list[str] = []

    def add(q: str) -> None:
        q = (q or "").strip().strip(",")
        if len(q) > 3 and q not in variantes:
            variantes.append(q)

    add(texto)
    normalizado = re.sub(r"\s+-\s+", ", ", texto)
    if normalizado != texto:
        add(normalizado)

    sem_cep = CEP_RE.sub("", texto).strip(" ,")
    if sem_cep and sem_cep != texto:
        add(sem_cep)
        add(re.sub(r"\s+-\s+", ", ", sem_cep))

    for base in list(variantes):
        if "brasil" not in base.lower() and "brazil" not in base.lower():
            add(f"{base}, Brasil")
    return variantes


def _nominatim_search(query: str, limit: int) -> list[dict]:
    try:
        response = requests.get(
            f"{NOMINATIM_BASE}/search",
            params={
                "q": query,
                "format": "json",
                "addressdetails": 1,
                "limit": limit,
                "countrycodes": "br",
                "viewbox": VIEWBOX_REGIAO_PADRAO,
                "bounded": "0",
            },
            headers=_headers(),
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        items = response.json()
    except requests.RequestException as exc:
        logger.warning("Nominatim search falhou (%s): %s", query[:80], exc)
        return []

    resultados = []
    for item in items:
        resultados.append(
            {
                "endereco_completo": item.get("display_name", query),
                "latitude": float(item["lat"]),
                "longitude": float(item["lon"]),
                "relevancia": float(item.get("importance", 0.5)),
            }
        )
    return resultados


def search_address(query: str, limit: int = 5) -> list[dict]:
    if not (query or "").strip():
        return []

    vistos: set[tuple[float, float]] = set()
    agregado: list[dict] = []

    for variante in _expand_search_queries(query):
        for item in _nominatim_search(variante, limit):
            chave = (round(item["latitude"], 5), round(item["longitude"], 5))
            if chave in vistos:
                continue
            vistos.add(chave)
            agregado.append(item)
        if agregado:
            break

    agregado.sort(key=lambda x: x.get("relevancia", 0), reverse=True)
    return agregado[:limit]
