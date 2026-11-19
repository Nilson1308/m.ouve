"""Geocodificação gratuita via Nominatim (OpenStreetMap)."""

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

NOMINATIM_BASE = "https://nominatim.openstreetmap.org"
DEFAULT_TIMEOUT = 12


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


def search_address(query: str, limit: int = 5) -> list[dict]:
    if not (query or "").strip():
        return []
    try:
        response = requests.get(
            f"{NOMINATIM_BASE}/search",
            params={
                "q": query,
                "format": "json",
                "addressdetails": 1,
                "limit": limit,
                "countrycodes": "br",
            },
            headers=_headers(),
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        items = response.json()
    except requests.RequestException as exc:
        logger.warning("Nominatim search falhou: %s", exc)
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
