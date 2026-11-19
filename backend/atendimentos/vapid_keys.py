"""VAPID — leitura da chave pública e geração (Application Server Key)."""

from __future__ import annotations

import os
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from django.conf import settings
from py_vapid import Vapid, b64urlencode


def application_server_key_b64(vapid: Vapid) -> str:
    """Converte a chave pública EC para o formato ``applicationServerKey`` (base64url)."""
    raw_pub = vapid.public_key.public_bytes(
        serialization.Encoding.X962,
        serialization.PublicFormat.UncompressedPoint,
    )
    return b64urlencode(raw_pub)


def get_configured_vapid_public_key() -> str | None:
    """
    Retorna ``VAPID_PUBLIC_KEY`` do settings ou deriva a partir de arquivo PEM
    (``VAPID_PRIVATE_KEY`` como caminho).
    """
    pub = (getattr(settings, "VAPID_PUBLIC_KEY", None) or "").strip()
    if pub:
        return pub

    private = (getattr(settings, "VAPID_PRIVATE_KEY", None) or "").strip()
    if private and os.path.isfile(private):
        try:
            vapid = Vapid.from_file(private_key_file=private)
            return application_server_key_b64(vapid)
        except Exception:
            return None
    return None


def generate_vapid_keypair(output_dir: Path, *, force: bool = False) -> tuple[Path, Path, str]:
    """
    Gera ``private_key.pem`` e ``public_key.pem`` em ``output_dir``.
    Retorna (private_path, public_path, application_server_key).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    private_path = output_dir / "private_key.pem"
    public_path = output_dir / "public_key.pem"

    if not force and (private_path.exists() or public_path.exists()):
        raise FileExistsError(
            f"Já existem chaves em {output_dir}. Use --force para sobrescrever."
        )

    vapid = Vapid()
    vapid.generate_keys()
    vapid.save_key(str(private_path))
    vapid.save_public_key(str(public_path))
    app_key = application_server_key_b64(vapid)
    return private_path, public_path, app_key