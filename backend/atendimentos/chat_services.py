"""Orquestração de chat (sessão stateful + motor LLM + anexos)."""

from __future__ import annotations

import logging
import mimetypes
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from atendimentos.chat_estado import FaseChat, get_fase, set_meta
from atendimentos.chat_resumo import montar_descricao_protocolo
from atendimentos.llm_orchestrator import (
    ChatOrchestrationError,
    LLMOrchestrator,
    MSG_REVISAO,
    TurnResult,
    _avaliar_regras_elegibilidade,
    _campos_faltantes,
    _dados_negocio,
    _exige_foto,
    _localizacao_ok,
    _msg_foto_servico,
    _msg_localizacao_servico,
    _qtd_anexos,
)
from atendimentos.models import AnexoChatSessao, AnexoProtocolo, MensagemChat, Protocolo, SessaoChat
from catalogo.validators import validar_dados_dinamicos
from rest_framework import serializers as drf_serializers

logger = logging.getLogger(__name__)

TIPO_ACAO_MAX_LEN = 255


def _sanitizar_tipo_acao(acao: str | None) -> str | None:
    if acao is None:
        return None
    valor = (acao or "").strip()
    if not valor:
        return None
    if len(valor) > TIPO_ACAO_MAX_LEN:
        logger.warning("tipo_acao truncado (%s chars): %s", len(valor), valor[:80])
        return valor[:TIPO_ACAO_MAX_LEN]
    return valor


class ChatProcessamentoError(Exception):
    """Falha recuperável no processamento assíncrono da IA."""


MSG_BOAS_VINDAS = (
    "Olá! Sou o assistente do M.Ouve. Descreva o que você precisa em suas próprias palavras "
    "e eu vou identificar o serviço certo e coletar as informações para o protocolo."
)


def titulo_categoria(categoria_inicial: str) -> str:
    return (categoria_inicial or "Atendimento").replace("_", " ").strip().title()


def criar_sessao_com_boas_vindas(usuario, categoria_inicial: str) -> tuple[SessaoChat, MensagemChat]:
    with transaction.atomic():
        sessao = SessaoChat.objects.create(
            usuario=usuario,
            categoria_inicial=(categoria_inicial or "").strip(),
            dados_coletados={"_meta": {"fase": FaseChat.EXPLORACAO}},
        )
        categoria_label = titulo_categoria(sessao.categoria_inicial)
        texto = (
            f"{MSG_BOAS_VINDAS}\n\n"
            f"Você está na categoria **{categoria_label}**. Como posso ajudar?"
        )
        mensagem = MensagemChat.objects.create(
            sessao=sessao,
            autor=MensagemChat.Autor.SISTEMA,
            conteudo_texto=texto,
        )
    return sessao, mensagem


def _ponto_localizacao(latitude, longitude) -> Point | None:
    if latitude is None or longitude is None:
        return None
    try:
        return Point(float(longitude), float(latitude), srid=4326)
    except (TypeError, ValueError):
        return None


def _aplicar_localizacao_sessao(sessao: SessaoChat, *, ponto: Point | None, endereco: str) -> None:
    if not ponto:
        return
    dados = dict(sessao.dados_coletados or {})
    dados["_localizacao"] = {
        "latitude": ponto.y,
        "longitude": ponto.x,
        "endereco": (endereco or "").strip(),
    }
    sessao.dados_coletados = dados
    sessao.save(update_fields=["dados_coletados", "atualizado_em"])


def _merge_dados_sessao(sessao: SessaoChat, extraidos: dict | None) -> None:
    if not extraidos:
        return
    dados = dict(sessao.dados_coletados or {})
    for chave, valor in extraidos.items():
        if str(chave).startswith("_"):
            continue
        dados[chave] = valor
    sessao.dados_coletados = dados
    sessao.save(update_fields=["dados_coletados", "atualizado_em"])


def _persistir_anexos_sessao(
    sessao: SessaoChat,
    mensagem: MensagemChat,
    arquivos: list[UploadedFile],
) -> int:
    criados = 0
    for arq in arquivos:
        if not arq:
            continue
        mime = arq.content_type or mimetypes.guess_type(getattr(arq, "name", ""))[0] or ""
        AnexoChatSessao.objects.create(
            sessao=sessao,
            mensagem=mensagem,
            arquivo=arq,
            tipo_mime=mime[:120],
            nome_original=(arq.name or "")[:255],
        )
        criados += 1
    return criados


def _transferir_anexos_para_protocolo(sessao: SessaoChat, protocolo: Protocolo) -> None:
    for anexo in sessao.anexos_sessao.all():
        arquivo = anexo.arquivo
        AnexoProtocolo.objects.create(
            protocolo=protocolo,
            arquivo=arquivo,
            tipo_mime=anexo.tipo_mime or "application/octet-stream",
        )


def finalizar_sessao_com_protocolo(sessao: SessaoChat) -> Protocolo:
    servico = sessao.servico_identificado
    dados_brutos = {k: v for k, v in (sessao.dados_coletados or {}).items() if not str(k).startswith("_")}
    bloqueio = _avaliar_regras_elegibilidade(servico, dados_brutos)
    if bloqueio:
        raise drf_serializers.ValidationError(
            {"detalhe": bloqueio},
            code="elegibilidade",
        )
    try:
        dados_validados = validar_dados_dinamicos(servico.schema_formulario, dados_brutos)
    except drf_serializers.ValidationError:
        dados_validados = dados_brutos

    loc = (sessao.dados_coletados or {}).get("_localizacao") or {}
    protocolo = Protocolo(
        codigo=Protocolo.gerar_codigo(),
        usuario=sessao.usuario,
        servico=servico,
        dados_dinamicos=dados_validados,
        descricao=montar_descricao_protocolo(sessao),
        endereco_texto=(loc.get("endereco") or "")[:500],
        resposta_cidadao="",
        observacoes_internas="",
    )
    lat, lng = loc.get("latitude"), loc.get("longitude")
    if lat is not None and lng is not None:
        protocolo.localizacao = Point(float(lng), float(lat), srid=4326)
    from atendimentos.services.protocolo_localidade import sincronizar_localidade_protocolo

    sincronizar_localidade_protocolo(protocolo, persistir=False)
    protocolo.save()
    from atendimentos.services.triagem_service import executar_triagem_protocolo

    executar_triagem_protocolo(protocolo)
    _transferir_anexos_para_protocolo(sessao, protocolo)

    set_meta(sessao, fase=FaseChat.CONCLUIDO)
    sessao.status = SessaoChat.Status.FINALIZADO_PROTOCOLO
    sessao.protocolo_final = protocolo
    sessao.save(update_fields=["dados_coletados", "status", "protocolo_final", "atualizado_em"])
    return protocolo


def _resposta_parece_revisao(texto: str | None) -> bool:
    t = (texto or "").strip()
    return t == MSG_REVISAO or t.startswith("Aqui está o resumo")


def _rotulos_campos_faltantes(servico, campos: list[str]) -> str:
    if not servico or not campos:
        return ""
    props = (servico.schema_formulario or {}).get("properties") or {}
    labels = []
    for chave in campos:
        prop = props.get(chave) or {}
        labels.append((prop.get("title") or chave.replace("_", " ")).strip() or chave)
    return ", ".join(labels)


def _sincronizar_turno_revisao(sessao: SessaoChat, turno: TurnResult) -> None:
    """
    Garante que ``tipo_acao=revisao_final`` só acompanha resumo quando a sessão está pronta,
    e nunca envia o texto de revisão sem o card no PWA.
    """
    if not (turno.ir_para_revisao or turno.acao_ui == "revisao_final") or turno.fluxo_bloqueado:
        return

    servico = sessao.servico_identificado

    if _requisitos_revisao_ok(sessao):
        set_meta(sessao, fase=FaseChat.REVISAO)
        turno.acao_ui = "revisao_final"
        if not (turno.resposta_cidadao or "").strip():
            turno.resposta_cidadao = MSG_REVISAO
        sessao.save(update_fields=["dados_coletados", "atualizado_em"])
        return

    turno.ir_para_revisao = False

    if _resposta_parece_revisao(turno.resposta_cidadao):
        if servico and _exige_foto(servico) and _qtd_anexos(sessao) < 1:
            turno.resposta_cidadao = _msg_foto_servico(servico)
            turno.acao_ui = "solicitar_foto"
        elif servico and servico.exige_localizacao and not _localizacao_ok(sessao):
            turno.resposta_cidadao = _msg_localizacao_servico(servico)
            turno.acao_ui = "solicitar_localizacao"
        else:
            faltantes = _campos_faltantes(servico, _dados_negocio(sessao), sessao) if servico else []
            if faltantes:
                rotulos = _rotulos_campos_faltantes(servico, faltantes)
                turno.resposta_cidadao = (
                    f"Ainda preciso destas informações para montar o resumo: {rotulos}."
                )
            else:
                turno.resposta_cidadao = "Ainda faltam informações para concluir."
            turno.acao_ui = None
    elif servico:
        if _exige_foto(servico) and _qtd_anexos(sessao) < 1:
            turno.acao_ui = "solicitar_foto"
        elif servico.exige_localizacao and not _localizacao_ok(sessao):
            turno.acao_ui = "solicitar_localizacao"
        else:
            turno.acao_ui = None
    else:
        turno.acao_ui = None

    set_meta(sessao, fase=FaseChat.PREENCHIMENTO)
    sessao.save(update_fields=["dados_coletados", "atualizado_em"])


def _requisitos_revisao_ok(sessao: SessaoChat) -> bool:
    servico = sessao.servico_identificado
    if not servico:
        return False
    dados = _dados_negocio(sessao)
    if _campos_faltantes(servico, dados, sessao):
        return False
    if servico.exige_localizacao and not _localizacao_ok(sessao):
        return False
    if _exige_foto(servico) and _qtd_anexos(sessao) < 1:
        return False
    return True


def _aplicar_turno_llm(sessao: SessaoChat, turno: TurnResult) -> str | None:
    if turno.cancelar_servico_pendente:
        set_meta(
            sessao,
            fase=FaseChat.EXPLORACAO,
            servico_pendente_id=None,
        )
        sessao.save(update_fields=["dados_coletados", "atualizado_em"])

    if (
        turno.confirmar_servico
        and turno.servico_pendente_id
        and not turno.servico_id
        and not sessao.servico_identificado_id
    ):
        set_meta(
            sessao,
            fase=FaseChat.AGUARDANDO_CONFIRMACAO_SERVICO,
            servico_pendente_id=str(turno.servico_pendente_id),
        )
        sessao.save(update_fields=["dados_coletados", "atualizado_em"])

    if turno.servico_id:
        from catalogo.models import ServicoCatalogo

        servico = ServicoCatalogo.objects.filter(
            pk=turno.servico_id, ativo=True, is_template=False
        ).first()
        if servico:
            sessao.servico_identificado = servico
            set_meta(sessao, fase=FaseChat.PREENCHIMENTO, servico_pendente_id=None)
            sessao.save(
                update_fields=["servico_identificado", "dados_coletados", "atualizado_em"]
            )

    _merge_dados_sessao(sessao, turno.dados_extraidos)

    servico_turno = sessao.servico_identificado
    if servico_turno and (turno.ir_para_revisao or turno.acao_ui == "revisao_final"):
        from atendimentos.llm_orchestrator import _avaliar_regras_elegibilidade_detalhe

        bloqueio, motivo = _avaliar_regras_elegibilidade_detalhe(
            servico_turno, _dados_negocio(sessao)
        )
        if bloqueio:
            turno.fluxo_bloqueado = True
            turno.ir_para_revisao = False
            turno.acao_ui = None
            turno.resposta_cidadao = bloqueio
            turno.limpar_config_escolha = True
            turno.motivo_inelegibilidade = motivo

    if turno.fluxo_bloqueado and not turno.resposta_cidadao:
        turno.resposta_cidadao = (
            "Não foi possível dar continuidade a este atendimento com os dados informados."
        )

    if turno.fluxo_bloqueado:
        set_meta(sessao, fase=FaseChat.INELEGIVEL)
        motivo = (turno.motivo_inelegibilidade or "").strip()
        if not motivo and turno.resposta_cidadao:
            motivo = str(turno.resposta_cidadao).strip()[:255]
        sessao.motivo_inelegibilidade = motivo or None
        sessao.save(
            update_fields=["dados_coletados", "atualizado_em", "motivo_inelegibilidade"]
        )

    if turno.limpar_config_escolha:
        set_meta(sessao, pending_escolha=None)
        sessao.save(update_fields=["dados_coletados", "atualizado_em"])
    elif turno.config_escolha:
        set_meta(sessao, pending_escolha=turno.config_escolha)
        sessao.save(update_fields=["dados_coletados", "atualizado_em"])
    elif turno.dados_extraidos:
        set_meta(sessao, pending_escolha=None)
        sessao.save(update_fields=["dados_coletados", "atualizado_em"])

    _sincronizar_turno_revisao(sessao, turno)

    if turno.criar_protocolo and sessao.servico_identificado_id:
        if get_fase(sessao) != FaseChat.CONCLUIDO:
            set_meta(sessao, fase=FaseChat.REVISAO)
            sessao.save(update_fields=["dados_coletados", "atualizado_em"])
        try:
            protocolo = finalizar_sessao_com_protocolo(sessao)
            return protocolo.codigo
        except drf_serializers.ValidationError as exc:
            logger.warning("Protocolo não criado: %s", exc.detail)
    return None


def registrar_mensagem_cidadao(
    sessao: SessaoChat,
    *,
    texto: str,
    latitude=None,
    longitude=None,
    endereco: str = "",
    arquivos: list | None = None,
) -> tuple[MensagemChat, int]:
    """Persiste mensagem do cidadão, anexos e localização (sem LLM)."""
    texto = (texto or "").strip()
    ponto = _ponto_localizacao(latitude, longitude)
    arquivos = arquivos or []

    with transaction.atomic():
        msg_cidadao = MensagemChat.objects.create(
            sessao=sessao,
            autor=MensagemChat.Autor.CIDADAO,
            conteudo_texto=texto or "(sem texto)",
            localizacao=ponto,
        )
        qtd_anexos = _persistir_anexos_sessao(sessao, msg_cidadao, arquivos)
        sessao.refresh_from_db()
        _aplicar_localizacao_sessao(sessao, ponto=ponto, endereco=endereco)

    return msg_cidadao, qtd_anexos


def executar_processamento_ia(
    sessao: SessaoChat,
    *,
    msg_cidadao: MensagemChat,
    confirmar_protocolo: bool = False,
    dados_slot: dict | None = None,
) -> MensagemChat:
    """Turno do LLM (chamado via Celery)."""
    from atendimentos.models import AnexoChatSessao

    texto = (msg_cidadao.conteudo_texto or "").strip()
    if texto == "(sem texto)":
        texto = ""

    qtd_anexos = AnexoChatSessao.objects.filter(mensagem=msg_cidadao).count()
    orchestrator = LLMOrchestrator()
    protocolo_criado = None

    with transaction.atomic():
        sessao = SessaoChat.objects.select_for_update().get(pk=sessao.pk)

        try:
            from atendimentos.chat_escolhas import normalizar_dados_slot

            slot = None
            if dados_slot and sessao.servico_identificado_id:
                slot = normalizar_dados_slot(sessao.servico_identificado, dados_slot)

            turno = orchestrator.processar_turno(
                sessao,
                texto_usuario=texto,
                anexos_novos=qtd_anexos,
                confirmar_protocolo=confirmar_protocolo,
                dados_slot=slot,
            )
        except ChatOrchestrationError as exc:
            logger.warning("ChatOrchestrationError: %s", exc)
            texto_erro = str(exc).strip()
            if "limite de uso" in texto_erro.lower() or "aguarde" in texto_erro.lower():
                resposta_erro = texto_erro
            else:
                resposta_erro = (
                    "Não consegui processar sua mensagem com a IA no momento. "
                    "Tente novamente em instantes."
                )
            turno = TurnResult(resposta_cidadao=resposta_erro, acao_ui=None)

        codigo = _aplicar_turno_llm(sessao, turno)
        sessao.refresh_from_db()

        resposta = turno.resposta_cidadao
        acao_ui = turno.acao_ui

        if (
            turno.disparar_preenchimento_deterministico
            and not codigo
            and get_fase(sessao) == FaseChat.PREENCHIMENTO
        ):
            prefixo_slot = ""
            servico = sessao.servico_identificado
            if servico:
                from atendimentos.slot_filling_service import aplicar_slot_filling_abertura

                prefixo_slot, _ = aplicar_slot_filling_abertura(sessao, servico)
                sessao.refresh_from_db()

            det = orchestrator.passo_deterministico_preenchimento(sessao, anexos_novos=qtd_anexos)
            codigo_det = _aplicar_turno_llm(sessao, det)
            sessao.refresh_from_db()
            if codigo_det:
                codigo = codigo_det
            resposta = (det.resposta_cidadao or "").strip()
            if prefixo_slot and resposta and not det.fluxo_bloqueado:
                resposta = f"{prefixo_slot}\n\n{resposta}"
            elif prefixo_slot and not resposta and not det.fluxo_bloqueado:
                resposta = prefixo_slot
            acao_ui = det.acao_ui

        if codigo:
            resposta = f"{resposta}\n\nProtocolo **{codigo}** registrado com sucesso."
            protocolo_criado = sessao.protocolo_final
            acao_ui = "pesquisa_satisfacao"

        from atendimentos.chat_estado import get_pending_escolha

        payload_ui = None
        if acao_ui == "escolha_campo":
            payload_ui = get_pending_escolha(sessao)

        msg_ia = MensagemChat.objects.create(
            sessao=sessao,
            autor=MensagemChat.Autor.IA,
            conteudo_texto=resposta,
            tipo_acao=_sanitizar_tipo_acao(acao_ui),
            payload_ui=payload_ui,
        )

    from atendimentos.notificacoes_cidadao import notificar_resposta_ia_chat

    notificar_resposta_ia_chat(sessao, msg_ia)

    return msg_ia
