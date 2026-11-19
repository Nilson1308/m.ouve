"""Checagens de saúde Redis/Celery para monitoramento do chat (Super Admin)."""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime, timezone

from django.conf import settings

logger = logging.getLogger(__name__)

# inspect.ping() via Redis costuma levar 3–6s com vários workers no broker.
CHECAGEM_TIMEOUT_SEC = 10.0
CELERY_INSPECT_PING_SEC = 5.0
CELERY_INSPECT_FILAS_SEC = 4.0


def _agora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def verificar_redis() -> dict:
    """Ping na conexão Redis do broker Celery."""
    try:
        import redis

        url = (getattr(settings, "CELERY_BROKER_URL", "") or "").strip()
        if not url:
            return {
                "status": "OFFLINE",
                "ok": False,
                "detalhe": "CELERY_BROKER_URL não configurado",
            }
        client = redis.from_url(
            url,
            socket_connect_timeout=3.0,
            socket_timeout=3.0,
        )
        client.ping()
        return {"status": "ONLINE", "ok": True, "detalhe": None}
    except Exception as exc:
        logger.warning("Saúde Redis: %s", exc)
        return {"status": "OFFLINE", "ok": False, "detalhe": str(exc)[:240]}


def _inspecionar_celery() -> dict:
    from ouvia_core.celery import app

    fila_padrao = getattr(settings, "CELERY_TASK_DEFAULT_QUEUE", None) or "ouve"

    insp_ping = app.control.inspect(timeout=CELERY_INSPECT_PING_SEC)
    ping = insp_ping.ping() if insp_ping else None
    ping = ping or {}
    workers_ping = sorted(ping.keys())
    workers_vivos_ping = len(workers_ping)

    filas: set[str] = set()
    workers_fila_projeto: list[str] = []
    active_queues: dict = {}
    if workers_vivos_ping:
        try:
            insp_filas = app.control.inspect(timeout=CELERY_INSPECT_FILAS_SEC)
            active_queues = insp_filas.active_queues() if insp_filas else {}
            active_queues = active_queues or {}
            for worker_name, qlist in active_queues.items():
                nomes_fila: list[str] = []
                for item in qlist or []:
                    if isinstance(item, dict):
                        nome = (item.get("name") or "").strip()
                        if nome:
                            filas.add(nome)
                            nomes_fila.append(nome)
                if fila_padrao in nomes_fila:
                    workers_fila_projeto.append(worker_name)
        except Exception as exc:
            logger.debug("active_queues indisponível: %s", exc)

    if workers_fila_projeto:
        ok = True
        workers = sorted(workers_fila_projeto)
        workers_vivos = len(workers)
    elif workers_vivos_ping > 0:
        ok = True
        workers = workers_ping
        workers_vivos = workers_vivos_ping
    else:
        ok = False
        workers = []
        workers_vivos = 0

    detalhe = None
    if not ok:
        detalhe = "Nenhum worker Celery respondeu ao ping"
    elif fila_padrao not in filas and filas:
        detalhe = (
            f"Há workers no broker, mas nenhum na fila «{fila_padrao}». "
            "Confirme celery-ouve.service (-Q ouve)."
        )
    elif workers_vivos_ping and not filas:
        detalhe = "Workers respondendo; filas não listadas (inspect lento ou indisponível)."

    return {
        "status": "ONLINE" if ok else "OFFLINE",
        "ok": ok,
        "workers_vivos": workers_vivos,
        "workers": workers,
        "filas_detectadas": sorted(filas),
        "fila_padrao": fila_padrao,
        "workers_fila_projeto": sorted(workers_fila_projeto),
        "detalhe": detalhe,
    }


def verificar_celery() -> dict:
    """Inspeção Celery com timeout para não bloquear a requisição HTTP."""
    base_offline = {
        "status": "OFFLINE",
        "ok": False,
        "workers_vivos": 0,
        "workers": [],
        "filas_detectadas": [],
        "fila_padrao": getattr(settings, "CELERY_TASK_DEFAULT_QUEUE", None) or "ouve",
        "workers_fila_projeto": [],
    }
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            fut = pool.submit(_inspecionar_celery)
            return fut.result(timeout=CHECAGEM_TIMEOUT_SEC)
    except FuturesTimeoutError:
        return {
            **base_offline,
            "detalhe": f"Timeout após {CHECAGEM_TIMEOUT_SEC}s na inspeção Celery",
        }
    except Exception as exc:
        logger.warning("Saúde Celery: %s", exc)
        return {
            **base_offline,
            "detalhe": str(exc)[:240],
        }


def montar_relatorio_saude_infra() -> dict:
    redis = verificar_redis()
    celery = verificar_celery()
    chat_operacional = bool(redis.get("ok") and celery.get("ok"))
    return {
        "chat_operacional": chat_operacional,
        "redis": redis,
        "celery": celery,
        "verificado_em": _agora_iso(),
    }