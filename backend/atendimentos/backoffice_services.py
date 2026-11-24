"""Regras de negócio do backoffice (scatter-gather)."""

import uuid
from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.utils import timezone

from atendimentos.models import OrdemServico, Protocolo, ProtocoloHistorico, SuperOS

if TYPE_CHECKING:
    pass

STATUS_PROTOCOLO_ENCERRADO = frozenset(
    {
        Protocolo.Status.RESOLVIDO,
        Protocolo.Status.REJEITADO,
    }
)


class ProtocoloEncerradoError(ValueError):
    """Protocolo já concluído ou rejeitado — tramitação não permitida."""


def get_protocolo_backoffice(protocolo_ref, queryset=None, *, user=None):
    """
    Resolve protocolo por UUID (id) ou por código legível (ex.: PROT-2026-001).
    Com ``user``, aplica escopo de dados (404 se fora da unidade / IDOR).
    """
    from atendimentos.services.escopo_dados import aplicar_escopo_protocolos

    qs = queryset if queryset is not None else Protocolo.objects.all()
    if user is not None:
        qs = aplicar_escopo_protocolos(user, qs)
    ref = str(protocolo_ref).strip()
    try:
        uid = uuid.UUID(ref)
        return get_object_or_404(qs, pk=uid)
    except ValueError:
        return get_object_or_404(qs, codigo__iexact=ref)


def get_ordem_servico_backoffice(ordem_id, *, user=None):
    """Carrega ordem garantindo que o protocolo está no escopo do usuário."""
    ordem = get_object_or_404(
        OrdemServico.objects.select_related("protocolo", "unidade"),
        pk=ordem_id,
    )
    if user is not None:
        get_protocolo_backoffice(ordem.protocolo_id, user=user)
    return ordem


def protocolo_esta_encerrado(protocolo: Protocolo) -> bool:
    return protocolo.status in STATUS_PROTOCOLO_ENCERRADO


def garantir_protocolo_tramitavel(protocolo: Protocolo) -> None:
    """Impede despacho / validação em protocolo já encerrado."""
    if protocolo_esta_encerrado(protocolo):
        label = dict(Protocolo.Status.choices).get(protocolo.status, protocolo.status)
        raise ProtocoloEncerradoError(
            f"O protocolo {protocolo.codigo} já está encerrado ({label}). "
            "Não é possível tramitar ou validar novamente."
        )


def ordens_ativas(protocolo: Protocolo):
    return protocolo.ordens_servico.exclude(status=OrdemServico.Status.CANCELADA)


def ordens_ativas_escopo_operacional(protocolo: Protocolo):
    """
    Ordens que contam para o gather: as do protocolo ou, em Super OS, todas as OS do incidente.
    """
    if protocolo.super_os_id:
        return OrdemServico.objects.filter(super_os_id=protocolo.super_os_id).exclude(
            status=OrdemServico.Status.CANCELADA
        )
    return ordens_ativas(protocolo)


def todas_ordens_concluidas(protocolo: Protocolo) -> bool:
    qs = ordens_ativas_escopo_operacional(protocolo)
    if not qs.exists():
        qs = ordens_ativas(protocolo)
    if not qs.exists():
        return False
    return not qs.exclude(status=OrdemServico.Status.CONCLUIDA).exists()


def _resumir_texto(texto: str, limite: int = 500) -> str:
    limpo = (texto or "").strip()
    if len(limpo) <= limite:
        return limpo
    return limpo[: limite - 1] + "…"


def registrar_retorno_setor_para_validacao(
    protocolo: Protocolo,
    *,
    ordem: OrdemServico | None = None,
    unidade_nome: str = "",
    despacho_tecnico: str = "",
    equipe_nome: str = "",
) -> None:
    """
    Registra no histórico o retorno técnico do setor, sem encerrar o protocolo ao cidadão.
    """
    if protocolo_esta_encerrado(protocolo):
        return

    unidade = unidade_nome or (ordem.unidade.sigla or ordem.unidade.nome if ordem and ordem.unidade else "")
    equipe = equipe_nome or unidade
    momento = timezone.now().strftime("%d/%m/%Y %H:%M")
    trecho_despacho = _resumir_texto(despacho_tecnico or (ordem.despacho_tecnico if ordem else ""))

    partes = [
        f"Retorno do setor responsável ({unidade or 'unidade'}) em {momento}.",
        "Aguardando validação final pela Ouvidoria.",
    ]
    if trecho_despacho:
        partes.append(f"Parecer técnico: {trecho_despacho}")

    ProtocoloHistorico.objects.create(
        protocolo=protocolo,
        status=protocolo.status,
        descricao=" ".join(partes),
        equipe_nome=equipe,
    )


def _sincronizar_super_os_gather(super_os: SuperOS) -> None:
    """Quando todas as OS do incidente concluem, Super OS → aguardando_revisao."""
    if super_os.status in STATUS_PROTOCOLO_ENCERRADO:
        return
    qs = OrdemServico.objects.filter(super_os_id=super_os.pk).exclude(
        status=OrdemServico.Status.CANCELADA
    )
    if not qs.exists() or qs.exclude(status=OrdemServico.Status.CONCLUIDA).exists():
        return
    if super_os.status == Protocolo.Status.AGUARDANDO_REVISAO:
        return
    if super_os.status not in (
        Protocolo.Status.EM_ANDAMENTO,
        Protocolo.Status.EM_ANALISE,
    ):
        return

    super_os.status = Protocolo.Status.AGUARDANDO_REVISAO
    super_os.save(update_fields=["status", "atualizado_em"])

    from atendimentos.super_os_services import propagar_status_super_os_para_filhos

    propagar_status_super_os_para_filhos(super_os)


def tentar_aguardando_revisao(
    protocolo: Protocolo,
    *,
    equipe_nome: str = "",
    despacho_tecnico: str = "",
    ordem: OrdemServico | None = None,
    unidade_nome: str = "",
    registrar_evento_setor: bool = True,
) -> bool:
    """
    Transição gather: todas as OS do escopo operacional concluídas → aguardando_revisao.
    Nunca define ``resolvido`` — isso só na validação da Ouvidoria.
    """
    if protocolo_esta_encerrado(protocolo):
        return False

    if registrar_evento_setor and (despacho_tecnico or (ordem and ordem.despacho_tecnico)):
        registrar_retorno_setor_para_validacao(
            protocolo,
            ordem=ordem,
            unidade_nome=unidade_nome,
            despacho_tecnico=despacho_tecnico,
            equipe_nome=equipe_nome,
        )
        registrar_evento_setor = False

    if protocolo.status not in (
        Protocolo.Status.EM_ANDAMENTO,
        Protocolo.Status.EM_ANALISE,
    ):
        if protocolo.super_os_id:
            _sincronizar_super_os_gather(protocolo.super_os)
        return False

    if not todas_ordens_concluidas(protocolo):
        if protocolo.super_os_id:
            _sincronizar_super_os_gather(protocolo.super_os)
        protocolo.refresh_from_db()
        return protocolo.status == Protocolo.Status.AGUARDANDO_REVISAO

    protocolo.status = Protocolo.Status.AGUARDANDO_REVISAO
    protocolo.save(update_fields=["status", "data_atualizacao"])

    ProtocoloHistorico.objects.create(
        protocolo=protocolo,
        status=Protocolo.Status.AGUARDANDO_REVISAO,
        descricao=(
            "Todas as ordens de serviço foram concluídas. "
            "Protocolo aguardando validação e despacho final pela Ouvidoria."
        ),
        equipe_nome=equipe_nome or "",
    )

    if protocolo.super_os_id:
        _sincronizar_super_os_gather(protocolo.super_os)

    from atendimentos.notificacoes_cidadao import notificar_status_protocolo

    notificar_status_protocolo(protocolo, Protocolo.Status.AGUARDANDO_REVISAO)

    return True


def marcar_ordem_concluida(
    ordem: OrdemServico,
    *,
    observacoes: str = "",
    despacho_tecnico: str = "",
    observacoes_extras: str = "",
    formalizado_por=None,
    assinatura_hash: str = "",
    data_formalizacao=None,
) -> None:
    ordem.observacoes_execucao = observacoes.strip() or ordem.observacoes_execucao
    if despacho_tecnico:
        ordem.despacho_tecnico = despacho_tecnico.strip()
    if observacoes_extras:
        ordem.observacoes_extras = observacoes_extras.strip()
    if formalizado_por is not None:
        ordem.formalizado_por = formalizado_por
    if assinatura_hash:
        ordem.assinatura_digital_hash = assinatura_hash
    if data_formalizacao is not None:
        ordem.data_formalizacao = data_formalizacao
    ordem.status = OrdemServico.Status.CONCLUIDA
    ordem.concluido_em = timezone.now()
    update_fields = [
        "observacoes_execucao",
        "despacho_tecnico",
        "observacoes_extras",
        "formalizado_por",
        "assinatura_digital_hash",
        "status",
        "concluido_em",
        "atualizado_em",
    ]
    if data_formalizacao is not None:
        update_fields.append("data_formalizacao")
    ordem.save(update_fields=update_fields)


def concluir_atendimento_setor(
    protocolo: Protocolo,
    ordem: OrdemServico,
    *,
    despacho_tecnico: str = "",
    equipe_nome: str = "",
    unidade_nome: str = "",
) -> bool:
    """
    Após a OS ser marcada concluída: encerramento direto (direto_secretaria) ou homologação ouvidoria.
    """
    garantir_protocolo_tramitavel(protocolo)
    from atendimentos.services.fluxo_governanca_service import (
        servico_exige_validacao_ouvidoria,
        tentar_encerramento_direto_secretaria,
    )

    servico = protocolo.servico
    if servico and not servico_exige_validacao_ouvidoria(servico):
        if tentar_encerramento_direto_secretaria(
            protocolo,
            ordem=ordem,
            despacho_tecnico=despacho_tecnico,
            unidade_nome=unidade_nome,
        ):
            return True
        if not todas_ordens_concluidas(protocolo):
            registrar_retorno_setor_para_validacao(
                protocolo,
                ordem=ordem,
                unidade_nome=unidade_nome,
                despacho_tecnico=despacho_tecnico,
                equipe_nome=equipe_nome,
            )
            return False

    return tentar_aguardando_revisao(
        protocolo,
        equipe_nome=equipe_nome,
        despacho_tecnico=despacho_tecnico,
        ordem=ordem,
        unidade_nome=unidade_nome,
        registrar_evento_setor=True,
    )