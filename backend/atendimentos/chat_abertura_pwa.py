"""Abertura de sessão de chat — catálogo guiado e modos PWA (Sprint 4.9)."""

from __future__ import annotations

import uuid

from django.db import transaction
from rest_framework import serializers

from atendimentos.chat_estado import FaseChat, get_pending_escolha, set_meta
from atendimentos.chat_services import (
    _sanitizar_tipo_acao,
    criar_sessao_com_boas_vindas,
)
from atendimentos.llm_orchestrator import LLMOrchestrator
from atendimentos.models import ConfiguracaoSistema, MensagemChat, SessaoChat
from atendimentos.pwa_abertura import (
    CODE_SERVICO_OBRIGATORIO_GUIADO,
    MODO_ABERTURA_CATALOGO_GUIADO,
    ORIGEM_ABERTURA_CATALOGO_GUIADO,
    ORIGEM_ABERTURA_CHAT_IA,
)
from catalogo.models import ServicoCatalogo
from catalogo.pwa_catalogo import (
    categoria_coincide,
    queryset_servicos_pwa_publicados,
    servicos_visiveis_por_categoria,
)


def _obter_servico_pwa(servico_id: uuid.UUID) -> ServicoCatalogo:
    servico = (
        queryset_servicos_pwa_publicados().filter(pk=servico_id).select_related("categoria").first()
    )
    if not servico:
        raise serializers.ValidationError(
            {"servico_id": "Serviço indisponível, inativo ou não publicado no catálogo do PWA."}
        )
    return servico


def _criar_sessao_estagio2_catalogo(
    usuario,
    servico: ServicoCatalogo,
    categoria_inicial: str,
) -> tuple[SessaoChat, MensagemChat]:
    cat_sessao = (categoria_inicial or "").strip() or servico.categoria.slug
    with transaction.atomic():
        sessao = SessaoChat.objects.create(
            usuario=usuario,
            categoria_inicial=cat_sessao,
            servico_identificado=servico,
            origem_abertura=ORIGEM_ABERTURA_CATALOGO_GUIADO,
            dados_coletados={"_meta": {"fase": FaseChat.PREENCHIMENTO}},
        )
        from atendimentos.slot_filling_service import aplicar_slot_filling_abertura

        prefixo_slot, _ = aplicar_slot_filling_abertura(sessao, servico)
        sessao.refresh_from_db()
        turno = LLMOrchestrator().passo_deterministico_preenchimento(sessao)
        if turno.config_escolha:
            set_meta(sessao, pending_escolha=turno.config_escolha)
            sessao.save(update_fields=["dados_coletados", "atualizado_em"])
        elif turno.limpar_config_escolha:
            set_meta(sessao, pending_escolha=None)
            sessao.save(update_fields=["dados_coletados", "atualizado_em"])

        acolhimento = f"Certo! Vamos registrar sua solicitação de {servico.nome}."
        partes = [acolhimento]
        if (prefixo_slot or "").strip():
            partes.append(prefixo_slot.strip())
        if (turno.resposta_cidadao or "").strip():
            partes.append(turno.resposta_cidadao.strip())
        texto = "\n\n".join(partes)

        payload_ui = turno.payload_ui
        acao_ui = turno.acao_ui
        if acao_ui == "escolha_campo":
            payload_ui = get_pending_escolha(sessao)

        mensagem = MensagemChat.objects.create(
            sessao=sessao,
            autor=MensagemChat.Autor.IA,
            conteudo_texto=texto,
            tipo_acao=_sanitizar_tipo_acao(acao_ui),
            payload_ui=payload_ui,
        )
    return sessao, mensagem


def criar_sessao_chat_pwa(
    usuario,
    *,
    categoria_inicial: str,
    servico_id: uuid.UUID | None = None,
) -> tuple[SessaoChat, MensagemChat]:
    cfg = ConfiguracaoSistema.load()
    modo = cfg.modo_abertura_pwa
    cat = (categoria_inicial or "").strip()

    if servico_id:
        servico = _obter_servico_pwa(servico_id)
        if cat and not categoria_coincide(servico, cat):
            raise serializers.ValidationError(
                {
                    "categoria_inicial": (
                        "O serviço informado não pertence à categoria inicial indicada."
                    )
                }
            )
        if not cat:
            cat = servico.categoria.slug
        return _criar_sessao_estagio2_catalogo(usuario, servico, cat)

    if modo == MODO_ABERTURA_CATALOGO_GUIADO:
        visiveis = list(servicos_visiveis_por_categoria(cat).order_by("ordem_exibicao_pwa", "nome"))
        if len(visiveis) == 1:
            return _criar_sessao_estagio2_catalogo(usuario, visiveis[0], cat)
        raise serializers.ValidationError(
            {
                "code": CODE_SERVICO_OBRIGATORIO_GUIADO,
                "detail": (
                    "Neste modo, selecione o serviço na lista do catálogo antes de iniciar o atendimento."
                ),
            }
        )

    sessao, mensagem = criar_sessao_com_boas_vindas(usuario, cat)
    if sessao.origem_abertura != ORIGEM_ABERTURA_CHAT_IA:
        sessao.origem_abertura = ORIGEM_ABERTURA_CHAT_IA
        sessao.save(update_fields=["origem_abertura", "atualizado_em"])
    return sessao, mensagem