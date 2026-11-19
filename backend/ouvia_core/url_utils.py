"""URLs públicas absolutas (HTTPS atrás de proxy reverso)."""

from __future__ import annotations

from decouple import config
from django.http import HttpRequest


def public_absolute_uri(request: HttpRequest | None, location: str | None) -> str | None:
    if not location:
        return None

    public_base = config("PUBLIC_BASE_URL", default="").strip().rstrip("/")

    if location.startswith(("http://", "https://")):
        if location.startswith("http://") and public_base.startswith("https://"):
            return location.replace("http://", "https://", 1)
        return location

    path = location if location.startswith("/") else f"/{location}"

    if public_base:
        return f"{public_base}{path}"

    if request is not None:
        uri = request.build_absolute_uri(path)
        if request.is_secure() and uri.startswith("http://"):
            return uri.replace("http://", "https://", 1)
        forwarded = (request.META.get("HTTP_X_FORWARDED_PROTO") or "").split(",")[0].strip()
        if forwarded == "https" and uri.startswith("http://"):
            return uri.replace("http://", "https://", 1)
        return uri

    return path
