"""Transcrição de áudio (Groq Whisper / OpenAI-compat)."""

from __future__ import annotations

import os
import tempfile

from decouple import config
from django.core.files.uploadedfile import UploadedFile
from openai import OpenAI

from atendimentos.llm_orchestrator import _cliente_llm


def transcrever_upload_audio(arquivo: UploadedFile) -> tuple[str, float]:
    """Retorna (texto, confiança estimada)."""
    suffix = _suffix_por_mime(arquivo.content_type or "", arquivo.name or "")
    content_type = _content_type_para_upload(arquivo.content_type or "", suffix)
    client: OpenAI = _cliente_llm()
    model = config("GROQ_WHISPER_MODEL", default="whisper-large-v3-turbo")

    path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            path = tmp.name
            for chunk in arquivo.chunks():
                tmp.write(chunk)
            tmp.flush()

        with open(path, "rb") as audio_file:
            resultado = client.audio.transcriptions.create(
                model=model,
                file=(f"gravacao{suffix}", audio_file, content_type),
                language="pt",
            )
    finally:
        if path and os.path.exists(path):
            os.unlink(path)

    texto = (getattr(resultado, "text", None) or str(resultado)).strip()
    if not texto:
        raise ValueError("Nenhuma fala detectada no áudio.")
    return texto, 0.92


def _suffix_por_mime(content_type: str, nome_arquivo: str = "") -> str:
    mapping = {
        "audio/webm": ".webm",
        "audio/ogg": ".ogg",
        "audio/mpeg": ".mp3",
        "audio/mp3": ".mp3",
        "audio/mp4": ".m4a",
        "audio/wav": ".wav",
        "audio/x-wav": ".wav",
    }
    base = (content_type or "").split(";")[0].strip().lower()
    if base in mapping:
        return mapping[base]
    lower = (nome_arquivo or "").lower()
    for ext in (".webm", ".ogg", ".mp3", ".m4a", ".wav"):
        if lower.endswith(ext):
            return ext
    return ".webm"


def _content_type_para_upload(content_type: str, suffix: str) -> str:
    base = (content_type or "").split(";")[0].strip().lower()
    if base:
        return base
    return {
        ".webm": "audio/webm",
        ".ogg": "audio/ogg",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".wav": "audio/wav",
    }.get(suffix, "audio/webm")
