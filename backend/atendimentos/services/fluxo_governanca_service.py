"""Governança de entrada/saída por fluxo_tramitacao (Sprint 2.5)."""

from __future__ import annotations

import logging

from django.db import transaction

from atendimentos.backoffice_services import ordens_ativas, todas_ordens_concluidas
from atendimentos.models import OrdemServico, Protocolo, ProtocoloHistorico
from catalogo.models import ServicoCatalogo

logger = logging.getLogger(__name__)

FLUXO_HIBRIDO_LEGADO = "hibrido"


def servico_exige_validacao_ouvidoria(servico: ServicoCatalogo) -> bool:
    if servico.fluxo_tramitacao == ServicoCatalogo.FluxoTramitacao.OUVIDORIA_ENCAMINHA:
        return True
    return bool(servico.exigir_validacao_ouvidoria)


def encerramento_direto_secretaria_habilitado(protocolo: Protocolo) -> bool:
    """UI: botão «Concluir e responder ao cidadão» vs homologação ouvidoria."""
    servico = protocolo.servico
    if not servico_id_ok(servico):
        return False
    if servico.fluxo_tramitacao != ServicoCatalogo.FluxoTramitacao.DIRETO_SECRETARIA:
        return False
    if servico.exigir_validacao_ouvidoria:
        return False
    abertas = ordens_ativas(protocolo).exclude(
        status__in=(
            OrdemServico.Status.CONCLUIDA,
            OrdemServico.Status.CANCELADA,
        )
    )
    return abertas.count() <= 1


def servico_id_ok(servico) -> bool:
    return servico is not None and servico.pk is not None


def metadados_governanca_protocolo(protocolo: Protocolo) -> dict[str, bool]:
    servico = protocolo.servico
    return {
        "exigir_validacao_ouvidoria": servico_exige_validacao_ouvidoria(servico)
        if servico_id_ok(servico)
        else True,
        "encerramento_direto_secretaria": encerramento_direto_secretaria_habilitado(
            protocolo
        ),
    }


def _instrucao_padrao_os(protocolo: Protocolo) -> str:
    texto = (protocolo.descricao or "").strip()
    if texto:
        return texto[:2000]
    return f"Atendimento ao protocolo {protocolo.codigo}."


def _os_automatica_ja_existe(protocolo: Protocolo, unidade_id) -> bool:
    return ordens_ativas(protocolo).filter(unidade_id=unidade_id).exists()


@transaction.atomic
def processar_governanca_entrada_protocolo(protocolo: Protocolo) -> None:
    """
    Após criação do protocolo e triagem: auto-despacho no fluxo direto_secretaria.
    Idempotente por (protocolo, unidade executora).
    """
    protocolo = Protocolo.objects.select_for_update().get(pk=protocolo.pk)
    servico = ServicoCatalogo.objects.select_related("unidade_responsavel").get(
        pk=protocolo.servico_id
    )
    if servico.fluxo_tramitacao != ServicoCatalogo.FluxoTramitacao.DIRETO_SECRETARIA:
        return

    unidade = servico.unidade_responsavel
    if not unidade or not unidade.ativo:
        motivo = (
            "Unidade executora ausente ou inativa"
            if not unidade
            else f"Unidade executora inativa ({unidade.nome})"
        )
        ProtocoloHistorico.objects.create(
            protocolo=protocolo,
            status=protocolo.status,
            descricao=(
                f"Auto-despacho não realizado — {motivo}. "
                "Protocolo mantido em análise na Mesa da Ouvidoria."
            ),
            equipe_nome="Sistema",
        )
        return

    if _os_automatica_ja_existe(protocolo, unidade.id):
        if protocolo.status == Protocolo.Status.EM_ANALISE:
            protocolo.status = Protocolo.Status.EM_ANDAMENTO
            protocolo.save(update_fields=["status", "data_atualizacao"])
        return

    prazo = servico.sla_horas or 72
    ordem = OrdemServico.objects.create(
        protocolo=protocolo,
        unidade=unidade,
        descricao=_instrucao_padrao_os(protocolo),
        prazo_horas=prazo,
        nome_equipe=unidade.sigla or unidade.nome,
        status=OrdemServico.Status.PENDENTE,
        despachado_por=None,
    )

    protocolo.status = Protocolo.Status.EM_ANDAMENTO
    protocolo.save(update_fields=["status", "data_atualizacao"])

    ProtocoloHistorico.objects.create(
        protocolo=protocolo,
        status=Protocolo.Status.EM_ANDAMENTO,
        descricao=f"Despacho automático — fluxo direto para {unidade.nome}.",
        equipe_nome="Sistema",
    )

    from atendimentos.notificacoes_internas import notificar_despacho_scatter

    notificar_despacho_scatter(protocolo, [ordem])

    from atendimentos.notificacoes_cidadao import notificar_status_protocolo

    notificar_status_protocolo(protocolo, Protocolo.Status.EM_ANDAMENTO)


def tentar_encerramento_direto_secretaria(
    protocolo: Protocolo,
    *,
    ordem: OrdemServico | None = None,
    despacho_tecnico: str = "",
    unidade_nome: str = "",
) -> bool:
    """Encerra protocolo ao cidadão sem fila de homologação da Ouvidoria."""
    protocolo.refresh_from_db()
    servico = protocolo.servico
    if servico.fluxo_tramitacao != ServicoCatalogo.FluxoTramitacao.DIRETO_SECRETARIA:
        return False
    if servico.exigir_validacao_ouvidoria:
        return False
    if not todas_ordens_concluidas(protocolo):
        return False

    parecer = (despacho_tecnico or "").strip()
    if not parecer and ordem:
        parecer = (ordem.despacho_tecnico or ordem.observacoes_execucao or "").strip()
    if not parecer:
        unidade = unidade_nome or (
            (ordem.unidade.sigla or ordem.unidade.nome) if ordem and ordem.unidade else ""
        )
        parecer = (
            f"Atendimento concluído pela unidade executora{f' ({unidade})' if unidade else ''}."
        )

    protocolo.resposta_cidadao = parecer
    protocolo.status = Protocolo.Status.RESOLVIDO
    protocolo.save(
        update_fields=["resposta_cidadao", "status", "data_atualizacao"]
    )

    unidade_label = unidade_nome or (
        (ordem.unidade.nome if ordem and ordem.unidade else "unidade executora")
    )
    ProtocoloHistorico.objects.create(
        protocolo=protocolo,
        status=Protocolo.Status.RESOLVIDO,
        descricao=(
            f"Concluído diretamente pela unidade executora {unidade_label}. "
            "Resposta oficial enviada ao cidadão."
        ),
        equipe_nome=unidade_label,
    )

    from atendimentos.notificacoes_cidadao import notificar_status_protocolo
    from atendimentos.services.reabertura_service import aplicar_janela_reabertura_apos_conclusao

    aplicar_janela_reabertura_apos_conclusao(protocolo)
    notificar_status_protocolo(protocolo, Protocolo.Status.RESOLVIDO)
    try:
        from atendimentos.services.agente_briefing_service import invalidar_cache_briefing_protocolo

        invalidar_cache_briefing_protocolo(protocolo)
    except Exception:
        pass
    return True