"""Criação e sincronização de status da Super OS com protocolos filhos."""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from catalogo.models import UnidadeAdministrativa

from atendimentos.cluster_services import (
    OS_ATIVA_CAMP,
    OS_ENCERRADA,
    STATUS_AGRUPAVEL_IA,
    centroide,
)
from atendimentos.models import OrdemServico, Protocolo, ProtocoloHistorico, SuperOS
from atendimentos.notificacoes_internas import notificar_despacho_super_os

MENSAGEM_RESOLUCAO_SUPER_OS = (
    "Seu relato foi atendido como parte de uma ação consolidada no local "
    "(Super OS). Agradecemos sua participação."
)

STATUS_PROPAGAR = frozenset(
    {
        Protocolo.Status.EM_ANDAMENTO,
        Protocolo.Status.AGUARDANDO_REVISAO,
        Protocolo.Status.RESOLVIDO,
        Protocolo.Status.REJEITADO,
    }
)


def _protocolo_tem_os_ativa(protocolo: Protocolo) -> bool:
    return protocolo.ordens_servico.exclude(status__in=OS_ENCERRADA).filter(
        status__in=OS_ATIVA_CAMP
    ).exists()


@transaction.atomic
def criar_super_os_a_partir_protocolos(
    protocolos_ids: list[str],
    titulo_resumo: str,
    descricao_geral: str = "",
) -> SuperOS:
    if not titulo_resumo or not titulo_resumo.strip():
        raise ValueError("titulo_resumo é obrigatório.")
    if not protocolos_ids:
        raise ValueError("Informe ao menos um protocolo.")

    protocolos = list(
        Protocolo.objects.select_for_update()
        .select_related("servico")
        .filter(pk__in=protocolos_ids)
    )
    if len(protocolos) != len(set(protocolos_ids)):
        raise ValueError("Um ou mais protocolos não foram encontrados.")

    sem_geo = [p.codigo for p in protocolos if not p.localizacao]
    if sem_geo:
        raise ValueError(
            f"Protocolos sem localização geográfica: {', '.join(sem_geo)}."
        )

    ja_agrupados = [p.codigo for p in protocolos if p.super_os_id]
    if ja_agrupados:
        raise ValueError(
            f"Protocolos já vinculados a outra Super OS: {', '.join(ja_agrupados)}."
        )

    com_os_ativa = [p.codigo for p in protocolos if _protocolo_tem_os_ativa(p)]
    if com_os_ativa:
        raise ValueError(
            "Existe ordem de serviço ativa no cluster "
            f"({', '.join(com_os_ativa)}). Use agrupamento retroativo "
            "com âncora operacional (POST .../super-os/retroativa), "
            "não crie Super OS em análise."
        )

    status_invalidos = [
        p.codigo
        for p in protocolos
        if p.status not in STATUS_AGRUPAVEL_IA
    ]
    if status_invalidos:
        raise ValueError(
            "Protocolos não elegíveis ao agrupamento (serviço de campo já concluído "
            f"ou encerrado): {', '.join(status_invalidos)}."
        )

    lat, lon = centroide(protocolos)
    if not descricao_geral.strip():
        trechos = [p.descricao.strip()[:200] for p in protocolos if p.descricao.strip()]
        descricao_geral = "\n\n---\n\n".join(trechos[:15])

    super_os = SuperOS.objects.create(
        codigo=SuperOS.gerar_codigo(),
        titulo_resumo=titulo_resumo.strip(),
        descricao_geral=descricao_geral.strip(),
        status=Protocolo.Status.EM_ANALISE,
        latitude_centro=lat,
        longitude_centro=lon,
    )

    for protocolo in protocolos:
        protocolo.super_os = super_os
        protocolo.save(update_fields=["super_os", "data_atualizacao"])
        ProtocoloHistorico.objects.create(
            protocolo=protocolo,
            status=protocolo.status,
            descricao=f"Agrupado na Super OS {super_os.codigo} ({super_os.titulo_resumo}).",
            equipe_nome="Mesa de Trabalho",
        )

    from atendimentos.services.matriz_urgencia_service import avaliar_escalonamento_super_os

    avaliar_escalonamento_super_os(super_os)
    return super_os


def propagar_status_super_os_para_filhos(super_os: SuperOS) -> int:
    """
    Espelha o status da Super OS nos protocolos filhos.
    Retorna quantidade de protocolos atualizados.
    """
    if super_os.status not in STATUS_PROPAGAR:
        return 0

    filhos = list(super_os.protocolos_filhos.select_related("usuario"))
    atualizados = 0
    agora = timezone.now()

    for protocolo in filhos:
        if protocolo.status == super_os.status:
            continue
        protocolo.status = super_os.status
        update_fields = ["status", "data_atualizacao"]
        if super_os.status == Protocolo.Status.RESOLVIDO:
            if not (protocolo.resposta_cidadao or "").strip():
                protocolo.resposta_cidadao = MENSAGEM_RESOLUCAO_SUPER_OS
                update_fields.append("resposta_cidadao")
        protocolo.save(update_fields=update_fields)
        ProtocoloHistorico.objects.create(
            protocolo=protocolo,
            status=protocolo.status,
            descricao=(
                f"Status atualizado pela Super OS {super_os.codigo} "
                f"({dict(Protocolo.Status.choices).get(protocolo.status, protocolo.status)})."
            ),
            equipe_nome="Super OS",
        )
        atualizados += 1

    if atualizados:
        super_os.atualizado_em = agora
        super_os.save(update_fields=["atualizado_em"])

    return atualizados


@transaction.atomic
def despachar_super_os(
    super_os: SuperOS,
    ordens_payload: list[dict],
    *,
    observacao_geral: str = "",
    despachado_por=None,
    request=None,
) -> tuple[SuperOS, list[OrdemServico]]:
    if super_os.status != Protocolo.Status.EM_ANALISE:
        raise ValueError(
            "Somente Super OS em análise podem ser despachadas "
            f"(status atual: {super_os.status})."
        )

    if super_os.ordens_servico.exclude(
        status=OrdemServico.Status.CANCELADA
    ).exists():
        raise ValueError("Esta Super OS já possui ordens de serviço ativas.")

    filhos = list(
        super_os.protocolos_filhos.select_related("servico").order_by("data_criacao")
    )
    if not filhos:
        raise ValueError("Super OS sem protocolos filhos vinculados.")

    if not ordens_payload:
        raise ValueError("Informe ao menos uma ordem de serviço no despacho.")

    unidade_ids = [item["unidade_id"] for item in ordens_payload]
    if len(unidade_ids) != len(set(unidade_ids)):
        raise ValueError("Cada unidade só pode receber uma ordem por despacho.")

    unidades = {
        u.id: u
        for u in UnidadeAdministrativa.objects.filter(pk__in=unidade_ids, ativo=True)
    }
    faltantes = [str(uid) for uid in unidade_ids if uid not in unidades]
    if faltantes:
        raise ValueError(
            f"Unidade administrativa inválida ou inativa: {', '.join(faltantes)}."
        )

    protocolo_referencia = filhos[0]
    ordens_criadas: list[OrdemServico] = []
    for item in ordens_payload:
        unidade = unidades[item["unidade_id"]]
        ordem = OrdemServico.objects.create(
            protocolo=protocolo_referencia,
            super_os=super_os,
            unidade=unidade,
            descricao=item["instrucao"],
            prazo_horas=item["prazo_horas"],
            nome_equipe=unidade.sigla or unidade.nome,
            status=OrdemServico.Status.PENDENTE,
            despachado_por=despachado_por,
        )
        ordens_criadas.append(ordem)

    obs = (observacao_geral or "").strip()
    if obs:
        bloco = f"Observação geral do despacho: {obs}"
        super_os.descricao_geral = (
            f"{super_os.descricao_geral}\n\n{bloco}".strip()
            if super_os.descricao_geral
            else bloco
        )

    super_os.status = Protocolo.Status.EM_ANDAMENTO
    super_os.save(update_fields=["status", "descricao_geral", "atualizado_em"])

    equipe = getattr(despachado_por, "nome", "") if despachado_por else ""
    descricao_hist = (
        f"Despacho Super OS {super_os.codigo} com {len(ordens_criadas)} ordem(ns)."
    )
    if obs:
        descricao_hist += f" Observação: {obs}"

    for protocolo in filhos:
        ProtocoloHistorico.objects.create(
            protocolo=protocolo,
            status=Protocolo.Status.EM_ANDAMENTO,
            descricao=descricao_hist,
            equipe_nome=equipe or "Mesa de Trabalho",
        )

    notificar_despacho_super_os(super_os, ordens_criadas, request=request)

    return super_os, ordens_criadas


@transaction.atomic
def anexar_protocolo_a_super_os(super_os: SuperOS, protocolo_id: str) -> Protocolo:
    """
    Vincula um protocolo a uma Super OS existente e espelha o status operacional.
    Protocolos anexados herdam as ordens de serviço já despachadas na Super OS.
    """
    if super_os.status not in STATUS_AGRUPAVEL_IA:
        raise ValueError(
            "Não é possível anexar protocolos a uma Super OS com serviço de campo "
            f"concluído ou em revisão (status: {super_os.status})."
        )

    protocolo = (
        Protocolo.objects.select_for_update()
        .select_related("servico")
        .filter(pk=protocolo_id)
        .first()
    )
    if not protocolo:
        raise ValueError("Protocolo não encontrado.")

    if protocolo.super_os_id:
        if protocolo.super_os_id == super_os.id:
            return protocolo
        raise ValueError(
            f"Protocolo {protocolo.codigo} já está vinculado à Super OS "
            f"{protocolo.super_os.codigo}."
        )

    if protocolo.status not in STATUS_AGRUPAVEL_IA:
        raise ValueError(
            f"Protocolo {protocolo.codigo} não pode ser agrupado no status atual "
            f"({protocolo.status})."
        )

    if not protocolo.localizacao:
        raise ValueError(f"Protocolo {protocolo.codigo} sem localização geográfica.")

    filhos = list(super_os.protocolos_filhos.only("servico_id"))
    if filhos:
        servicos_existentes = {f.servico_id for f in filhos if f.servico_id}
        if servicos_existentes and protocolo.servico_id not in servicos_existentes:
            raise ValueError(
                "O serviço do protocolo difere dos relatos já agrupados nesta Super OS."
            )

    protocolo.super_os = super_os
    protocolo.status = super_os.status
    update_fields = ["super_os", "status", "data_atualizacao"]
    if super_os.status == Protocolo.Status.RESOLVIDO:
        if not (protocolo.resposta_cidadao or "").strip():
            protocolo.resposta_cidadao = MENSAGEM_RESOLUCAO_SUPER_OS
            update_fields.append("resposta_cidadao")
    protocolo.save(update_fields=update_fields)

    ProtocoloHistorico.objects.create(
        protocolo=protocolo,
        status=protocolo.status,
        descricao=(
            f"Anexado à Super OS {super_os.codigo} ({super_os.titulo_resumo}). "
            "Status sincronizado com o incidente mestre — sem novo despacho individual."
        ),
        equipe_nome="Mesa de Trabalho",
    )

    if super_os.protocolos_filhos.exists():
        lat, lon = centroide(list(super_os.protocolos_filhos.filter(localizacao__isnull=False)))
        if lat is not None and lon is not None:
            super_os.latitude_centro = lat
            super_os.longitude_centro = lon
            super_os.save(update_fields=["latitude_centro", "longitude_centro", "atualizado_em"])

    from atendimentos.services.matriz_urgencia_service import avaliar_escalonamento_super_os

    avaliar_escalonamento_super_os(super_os)
    return protocolo


@transaction.atomic
def criar_super_os_retroativa(
    protocolo_ancora_id: str,
    protocolos_novos_ids: list[str],
    titulo_resumo: str,
    descricao_geral: str = "",
) -> SuperOS:
    """
    Super OS retroativa: envolve protocolo âncora (já despachado) e novos relatos,
    migra ordens de serviço ativas da âncora para o incidente mestre.
    """
    if not titulo_resumo or not titulo_resumo.strip():
        raise ValueError("titulo_resumo é obrigatório.")
    if not protocolos_novos_ids:
        raise ValueError("Informe ao menos um protocolo para anexar à âncora.")

    ancora = (
        Protocolo.objects.select_for_update()
        .select_related("servico")
        .filter(pk=protocolo_ancora_id)
        .first()
    )
    if not ancora:
        raise ValueError("Protocolo âncora não encontrado.")

    if ancora.super_os_id:
        raise ValueError(
            f"Âncora {ancora.codigo} já pertence à Super OS {ancora.super_os.codigo}. "
            "Use POST .../anexar na Super OS existente."
        )

    ordens_ativas = list(
        ancora.ordens_servico.exclude(status__in=OS_ENCERRADA).filter(
            status__in=OS_ATIVA_CAMP
        )
    )
    if not ordens_ativas:
        raise ValueError(
            f"Âncora {ancora.codigo} não possui ordem de serviço ativa no Painel Setorial."
        )

    novos_ids = [str(uid) for uid in protocolos_novos_ids if str(uid) != str(ancora.id)]
    if not novos_ids:
        raise ValueError("Nenhum protocolo novo para agrupar.")

    novos = list(
        Protocolo.objects.select_for_update()
        .select_related("servico")
        .filter(pk__in=novos_ids)
    )
    if len(novos) != len(set(novos_ids)):
        raise ValueError("Um ou mais protocolos novos não foram encontrados.")

    for p in novos:
        if p.super_os_id:
            raise ValueError(f"Protocolo {p.codigo} já vinculado a outra Super OS.")
        if p.status not in STATUS_AGRUPAVEL_IA:
            raise ValueError(f"Protocolo {p.codigo} não elegível ao agrupamento.")
        if not p.localizacao:
            raise ValueError(f"Protocolo {p.codigo} sem localização.")
        if p.servico_id and ancora.servico_id and p.servico_id != ancora.servico_id:
            raise ValueError(
                f"Serviço de {p.codigo} difere do protocolo âncora {ancora.codigo}."
            )

    todos = [ancora, *novos]
    lat, lon = centroide(todos)
    if not descricao_geral.strip():
        trechos = [p.descricao.strip()[:200] for p in todos if p.descricao.strip()]
        descricao_geral = "\n\n---\n\n".join(trechos[:15])

    status_mestre = Protocolo.Status.EM_ANDAMENTO

    super_os = SuperOS.objects.create(
        codigo=SuperOS.gerar_codigo(),
        titulo_resumo=titulo_resumo.strip(),
        descricao_geral=descricao_geral.strip(),
        status=status_mestre,
        latitude_centro=lat,
        longitude_centro=lon,
    )

    for protocolo in todos:
        protocolo.super_os = super_os
        protocolo.status = status_mestre
        protocolo.save(update_fields=["super_os", "status", "data_atualizacao"])
        ProtocoloHistorico.objects.create(
            protocolo=protocolo,
            status=status_mestre,
            descricao=(
                f"Agrupamento retroativo na Super OS {super_os.codigo} "
                f"(âncora operacional {ancora.codigo})."
            ),
            equipe_nome="Mesa de Trabalho",
        )

    for ordem in ordens_ativas:
        ordem.super_os = super_os
        ordem.save(update_fields=["super_os", "atualizado_em"])

    from atendimentos.services.matriz_urgencia_service import avaliar_escalonamento_super_os

    avaliar_escalonamento_super_os(super_os)
    return super_os


def _filhos_com_os_ativa(super_os: SuperOS) -> list[tuple[Protocolo, list[OrdemServico]]]:
    out: list[tuple[Protocolo, list[OrdemServico]]] = []
    for p in super_os.protocolos_filhos.all():
        ordens = list(
            p.ordens_servico.exclude(status__in=OS_ENCERRADA).filter(
                status__in=OS_ATIVA_CAMP
            )
        )
        if ordens:
            out.append((p, ordens))
    return out


@transaction.atomic
def integrar_ancora_operacional_super_os(super_os: SuperOS) -> SuperOS:
    """
    Corrige Super OS criada antes da retroativa: migra OS do filho âncora,
    alinha status em andamento e vincula ordens ao incidente mestre.
    """
    super_os = SuperOS.objects.select_for_update().get(pk=super_os.pk)
    filhos_os = _filhos_com_os_ativa(super_os)
    if not filhos_os:
        raise ValueError(
            "Nenhum protocolo filho com ordem de serviço ativa para integrar."
        )

    ordens_migrar: list[OrdemServico] = []
    for _p, ordens in filhos_os:
        for ordem in ordens:
            if ordem.super_os_id != super_os.id:
                ordens_migrar.append(ordem)

    if not ordens_migrar and super_os.status == Protocolo.Status.EM_ANDAMENTO:
        if super_os.ordens_servico.exclude(status=OrdemServico.Status.CANCELADA).exists():
            return super_os
        raise ValueError("Super OS já integrada ou sem ordens elegíveis.")

    status_mestre = Protocolo.Status.EM_ANDAMENTO
    super_os.status = status_mestre
    super_os.save(update_fields=["status", "atualizado_em"])

    for ordem in ordens_migrar:
        ordem.super_os = super_os
        ordem.save(update_fields=["super_os", "atualizado_em"])

    for protocolo in super_os.protocolos_filhos.all():
        if protocolo.status != status_mestre and protocolo.status in STATUS_AGRUPAVEL_IA:
            protocolo.status = status_mestre
            protocolo.save(update_fields=["status", "data_atualizacao"])
            ProtocoloHistorico.objects.create(
                protocolo=protocolo,
                status=status_mestre,
                descricao=(
                    f"Integrado à OS em campo da Super OS {super_os.codigo} "
                    "(âncora operacional — sem novo despacho)."
                ),
                equipe_nome="Mesa de Trabalho",
            )

    return super_os


def super_os_precisa_integracao_ancora(super_os: SuperOS) -> bool:
    """True quando há OS ativa em filho mas o mestre ainda parece 'triagem'."""
    if super_os.status != Protocolo.Status.EM_ANALISE:
        return False
    filhos_os = _filhos_com_os_ativa(super_os)
    if not filhos_os:
        return False
    ordens_mestre = super_os.ordens_servico.exclude(
        status=OrdemServico.Status.CANCELADA
    ).exists()
    if ordens_mestre:
        return False
    return any(
        o.super_os_id != super_os.id for _p, ordens in filhos_os for o in ordens
    )