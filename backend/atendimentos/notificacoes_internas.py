"""Motor de notificações internas (servidores / backoffice)."""

from __future__ import annotations

from django.contrib.auth import get_user_model

from atendimentos.backoffice_serializers import calcular_sla
from atendimentos.models import ConfiguracaoSistema, OrdemServico, Protocolo, SuperOS
from atendimentos.servicos_notificacao import criar_notificacao_interna
from ouvia_core.url_utils import public_absolute_uri

User = get_user_model()

STATUS_ABERTOS_SLA = frozenset(
    {
        Protocolo.Status.EM_ANALISE,
        Protocolo.Status.EM_ANDAMENTO,
        Protocolo.Status.AGUARDANDO_REVISAO,
    }
)


def _link(path: str, request=None) -> str:
    return public_absolute_uri(request, path) or path


def notificar_nova_os_unidade(
    ordem: OrdemServico,
    *,
    request=None,
) -> int:
    """Scatter — avisa servidores staff da unidade recebedora."""
    if not ordem.unidade_id:
        return 0

    protocolo = ordem.protocolo
    super_os = ordem.super_os
    if super_os:
        codigo = super_os.codigo
        contexto = f"na Super OS {codigo}"
    else:
        codigo = protocolo.codigo if protocolo else str(ordem.pk)[:8]
        contexto = f"no protocolo {codigo}"
    unidade_nome = ordem.unidade.nome if ordem.unidade else "sua secretaria"

    destinatarios = User.objects.filter(
        is_staff=True,
        is_active=True,
        unidade_id=ordem.unidade_id,
    )

    titulo = f"Nova OS — {codigo}"
    mensagem = (
        f"Nova ordem de serviço atribuída à {unidade_nome} {contexto}."
    )
    link = _link("/backoffice/setorial", request)

    criadas = 0
    for usuario in destinatarios:
        if criar_notificacao_interna(
            usuario.pk, titulo, mensagem, link_acao=link
        ):
            criadas += 1
    return criadas


def notificar_os_formalizada_ouvidor(
    ordem: OrdemServico,
    *,
    request=None,
) -> bool:
    """Gather — avisa o servidor que despachou a OS original."""
    destinatario = ordem.despachado_por
    if not destinatario or not destinatario.is_active:
        return False

    protocolo = ordem.protocolo
    codigo = protocolo.codigo if protocolo else str(ordem.pk)[:8]
    unidade = ordem.unidade
    unidade_label = unidade.nome if unidade else "Secretaria"

    titulo = f"OS concluída — {codigo}"
    mensagem = (
        f"A ordem de serviço do protocolo {codigo} foi formalizada "
        f"pela {unidade_label}."
    )
    link = _link(f"/backoffice/protocolo/{codigo}", request)

    return bool(
        criar_notificacao_interna(
            destinatario.pk, titulo, mensagem, link_acao=link
        )
    )


def notificar_despacho_scatter(
    protocolo: Protocolo,
    ordens: list[OrdemServico],
    *,
    request=None,
) -> int:
    if not ConfiguracaoSistema.load().notificar_novos_despachos:
        return 0
    total = 0
    for ordem in ordens:
        total += notificar_nova_os_unidade(ordem, request=request)
    return total


def notificar_despacho_super_os(
    super_os: SuperOS,
    ordens: list[OrdemServico],
    *,
    request=None,
) -> int:
    if not ConfiguracaoSistema.load().notificar_novas_super_os:
        return 0
    total = 0
    for ordem in ordens:
        total += notificar_nova_os_unidade(ordem, request=request)
    return total


def notificar_sla_vencido_protocolos(*, request=None, limite: int = 200) -> int:
    """
    Job batch: alerta servidores sobre protocolos abertos com SLA vencido.

    Destinatários: ``despachado_por`` da última OS da mesa; se ausente, staff da
    unidade responsável do serviço (quando houver).
    """
    if not ConfiguracaoSistema.load().notificar_sla_vencido:
        return 0

    qs = (
        Protocolo.objects.filter(status__in=STATUS_ABERTOS_SLA)
        .select_related("servico", "servico__unidade_responsavel")
        .order_by("data_criacao")[:limite]
    )

    criadas = 0
    notificados_por_protocolo = set()

    for protocolo in qs:
        sla = calcular_sla(protocolo)
        if not sla.get("vencido"):
            continue

        destinatarios: set = set()
        ordem = (
            OrdemServico.objects.filter(protocolo_id=protocolo.pk, despachado_por__isnull=False)
            .select_related("despachado_por")
            .order_by("-criado_em")
            .first()
        )
        if ordem and ordem.despachado_por_id and ordem.despachado_por.is_active:
            destinatarios.add(ordem.despachado_por_id)
        elif protocolo.servico_id and protocolo.servico.unidade_responsavel_id:
            for uid in User.objects.filter(
                is_active=True,
                is_staff=True,
                unidade_id=protocolo.servico.unidade_responsavel_id,
            ).values_list("id", flat=True):
                destinatarios.add(uid)

        if not destinatarios:
            continue

        titulo = f"SLA vencido — {protocolo.codigo}"
        mensagem = (
            f"O protocolo {protocolo.codigo} ultrapassou o prazo de SLA "
            f"({sla.get('sla_horas', 72)}h). Verifique na mesa de trabalho."
        )
        link = _link(f"/backoffice/protocolo/{protocolo.codigo}", request)

        for uid in destinatarios:
            chave = (protocolo.codigo, uid)
            if chave in notificados_por_protocolo:
                continue
            notificados_por_protocolo.add(chave)
            if criar_notificacao_interna(uid, titulo, mensagem, link_acao=link):
                criadas += 1

    return criadas
