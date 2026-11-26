"""Tarefas Celery — chat LLM e notificações push."""

from __future__ import annotations

import logging

from celery import shared_task
from django.db import transaction

from atendimentos.models import MensagemChat, SessaoChat
from atendimentos.notificacoes_service import registrar_envio_push_simulado

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=5)
def processar_mensagem_ia(
    self,
    sessao_id: str,
    mensagem_cidadao_id: str,
    confirmar_protocolo: bool = False,
    dados_slot: dict | None = None,
) -> str | None:
    """
    Processa o turno do LLM após mensagem do cidadão persistida.
    Retorna o ID da mensagem da IA (se criada).
    """
    from atendimentos.chat_services import ChatProcessamentoError, executar_processamento_ia

    try:
        sessao = SessaoChat.objects.get(pk=sessao_id)
    except SessaoChat.DoesNotExist:
        logger.error("Sessão de chat inexistente: %s", sessao_id)
        return None

    try:
        msg_cidadao = MensagemChat.objects.get(pk=mensagem_cidadao_id, sessao=sessao)
    except MensagemChat.DoesNotExist:
        logger.error("Mensagem cidadão %s não encontrada na sessão %s", mensagem_cidadao_id, sessao_id)
        return None

    try:
        msg_ia = executar_processamento_ia(
            sessao,
            msg_cidadao=msg_cidadao,
            confirmar_protocolo=confirmar_protocolo,
            dados_slot=dados_slot,
        )
        return str(msg_ia.id) if msg_ia else None
    except ChatProcessamentoError as exc:
        logger.warning("Falha ao processar IA (tentativa %s): %s", self.request.retries + 1, exc)
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        with transaction.atomic():
            MensagemChat.objects.create(
                sessao=sessao,
                autor=MensagemChat.Autor.IA,
                conteudo_texto=(
                    "Não consegui processar sua mensagem com a IA no momento. "
                    "Tente novamente em instantes."
                ),
                tipo_acao=None,
            )
        return None
    except Exception as exc:
        logger.exception("Erro inesperado ao processar mensagem IA: %s", exc)
        with transaction.atomic():
            MensagemChat.objects.create(
                sessao=sessao,
                autor=MensagemChat.Autor.IA,
                conteudo_texto=(
                    "Ocorreu um erro ao gerar a resposta. "
                    "Tente enviar a mensagem novamente."
                ),
                tipo_acao=None,
            )
        return None


@shared_task
def verificar_escalonamento_sla_task() -> int:
    from atendimentos.services.sla_cobranca_service import verificar_escalonamento_sla

    return verificar_escalonamento_sla()


@shared_task
def verificar_expiracao_diligencias_task() -> int:
    from atendimentos.services.diligencia_service import verificar_expiracao_diligencias

    return verificar_expiracao_diligencias()


@shared_task
def encerrar_janelas_reabertura_expiradas_task() -> int:
    from atendimentos.services.reabertura_service import encerrar_janelas_reabertura_expiradas

    return encerrar_janelas_reabertura_expiradas()


@shared_task
def gerar_briefings_operacionais_diarios_task() -> int:
    from atendimentos.services.agente_briefing_service import (
        gerar_briefings_operacionais_diarios,
    )

    return gerar_briefings_operacionais_diarios()


@shared_task
def enviar_digest_sla_atrasados_task() -> int:
    from atendimentos.services.sla_cobranca_service import (
        digest_agendado_se_aplica,
        enviar_digest_sla_atrasados,
    )

    if not digest_agendado_se_aplica():
        return 0
    envios = enviar_digest_sla_atrasados()
    return len(envios)


@shared_task
def notificar_sla_vencido_task() -> int:
    """Job Celery — alertas de SLA (respeita ``ConfiguracaoSistema.notificar_sla_vencido``)."""
    from atendimentos.notificacoes_internas import notificar_sla_vencido_protocolos

    return notificar_sla_vencido_protocolos()


@shared_task
def enviar_push_notification(
    usuario_id: str,
    titulo: str,
    corpo: str,
    dados_extras: dict | None = None,
) -> bool:
    """Legado — envio push simulado (preferir ``enviar_notificacao_push_task``)."""
    return registrar_envio_push_simulado(
        usuario_id=usuario_id,
        titulo=titulo,
        corpo=corpo,
        dados_extras=dados_extras,
    )


@shared_task(
    bind=True,
    max_retries=1,
    default_retry_delay=30,
    soft_time_limit=90,
    time_limit=120,
)
def executar_triagem_semantica_task(self, protocolo_id: str) -> dict | None:
    """Triagem semântica assíncrona (LLM) — enriquece ``triagem_sugerida`` sem bloquear o protocolo."""
    from atendimentos.services.triagem_service import executar_triagem_semantica_llm

    try:
        return executar_triagem_semantica_llm(protocolo_id)
    except Exception as exc:
        logger.warning(
            "Task triagem semântica falhou protocolo_id=%s: %s",
            protocolo_id,
            exc,
            exc_info=True,
        )
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc) from exc
        return None


@shared_task(bind=True, max_retries=2, default_retry_delay=15)
def enviar_notificacao_push_task(self, notificacao_id: str) -> dict:
    """Envia Web Push para inscrições do usuário a partir de ``NotificacaoCidadao``."""
    from atendimentos.notificacoes_push import enviar_push_para_notificacao

    try:
        return enviar_push_para_notificacao(notificacao_id)
    except Exception as exc:
        logger.exception("Falha na task de push notificacao_id=%s", notificacao_id)
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc) from exc
        return {"enviados": 0, "falhas": 1, "removidos": 0, "erro": str(exc)}
