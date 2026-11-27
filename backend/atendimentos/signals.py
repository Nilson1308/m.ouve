"""Sinais de protocolo — embedding, histórico e push."""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from atendimentos.models import ConfiguracaoSistema, Protocolo, ProtocoloHistorico, SuperOS
from atendimentos.super_os_services import propagar_status_super_os_para_filhos
from atendimentos.tasks import enviar_push_notification
from ia_orchestrator.tasks import gerar_embedding_solicitacao

_STATUS_LABEL = dict(Protocolo.Status.choices)


@receiver(pre_save, sender=Protocolo)
def protocolo_sincronizar_bairro(sender, instance, **kwargs):
    """Preenche ``dados_dinamicos.bairro`` quando há geo/endereço e o JSON ainda não tem."""
    from atendimentos.services.protocolo_localidade import (
        bairro_de_dados_dinamicos,
        sincronizar_localidade_protocolo,
    )

    if bairro_de_dados_dinamicos(instance.dados_dinamicos):
        return
    if not instance.localizacao and not (instance.endereco_texto or "").strip():
        return
    sincronizar_localidade_protocolo(instance, persistir=False)


@receiver(pre_save, sender=Protocolo)
def protocolo_guardar_status_anterior(sender, instance, **kwargs):
    if not instance.pk:
        instance._status_anterior = None  # type: ignore[attr-defined]
        return
    try:
        anterior = Protocolo.objects.only("status").get(pk=instance.pk)
        instance._status_anterior = anterior.status  # type: ignore[attr-defined]
    except Protocolo.DoesNotExist:
        instance._status_anterior = None  # type: ignore[attr-defined]


@receiver(post_save, sender=Protocolo)
def protocolo_criado(sender, instance, created, **kwargs):
    if created:
        ProtocoloHistorico.objects.create(
            protocolo=instance,
            status=instance.status,
            descricao="Protocolo criado",
        )
        gerar_embedding_solicitacao.delay(str(instance.id))
        return

    anterior = getattr(instance, "_status_anterior", None)
    if anterior and anterior != instance.status:
        titulo = "Atualização do seu protocolo"
        label = _STATUS_LABEL.get(instance.status, instance.status)
        if instance.status == Protocolo.Status.RESOLVIDO:
            titulo = "Seu protocolo foi concluído"
            trecho_resposta = (instance.resposta_cidadao or "").strip()
            if trecho_resposta:
                trecho = trecho_resposta[:160]
                if len(trecho_resposta) > 160:
                    trecho += "…"
                corpo = f"{instance.codigo}: {trecho}"
            else:
                corpo = (
                    f"O protocolo {instance.codigo} foi concluído. "
                    "Avalie nosso atendimento no aplicativo."
                )
        else:
            corpo = f"O protocolo {instance.codigo} agora está: {label}."
        extras = {
            "protocolo_id": str(instance.id),
            "protocolo_codigo": instance.codigo,
            "status": instance.status,
            "status_anterior": anterior,
        }
        if instance.status == Protocolo.Status.RESOLVIDO:
            extras["habilitar_avaliacao"] = True
        enviar_push_notification.delay(
            str(instance.usuario_id),
            titulo,
            corpo,
            extras,
        )


@receiver(pre_save, sender=SuperOS)
def super_os_guardar_status_anterior(sender, instance, **kwargs):
    if not instance.pk:
        instance._status_anterior = None  # type: ignore[attr-defined]
        return
    try:
        anterior = SuperOS.objects.only("status").get(pk=instance.pk)
        instance._status_anterior = anterior.status  # type: ignore[attr-defined]
    except SuperOS.DoesNotExist:
        instance._status_anterior = None  # type: ignore[attr-defined]


@receiver(post_save, sender=SuperOS)
def super_os_status_propagado(sender, instance, created, **kwargs):
    if created:
        return
    anterior = getattr(instance, "_status_anterior", None)
    if anterior is None or anterior == instance.status:
        return
    propagar_status_super_os_para_filhos(instance)


@receiver(post_save, sender=ConfiguracaoSistema)
def configuracao_sistema_invalida_config_pwa(sender, instance, **kwargs):
    from catalogo.pwa_catalogo import invalidar_cache_config_pwa

    invalidar_cache_config_pwa()
