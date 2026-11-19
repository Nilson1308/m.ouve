"""Tarefas Celery para NLP, embeddings e clusterização."""

import logging
import time

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="ia_orchestrator.gerar_embedding_solicitacao")
def gerar_embedding_solicitacao(protocolo_id: str):
    """
    Simula geração de embedding vetorial para RAG/clusterização.
    Futuramente integrará modelo de embeddings real.
    """
    logger.info("Iniciando embedding para protocolo %s", protocolo_id)
    time.sleep(2)
    logger.info("Embedding concluído (stub) para protocolo %s", protocolo_id)
    return {"protocolo_id": protocolo_id, "status": "ok"}
