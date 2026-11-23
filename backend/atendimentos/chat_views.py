"""Endpoints de orquestração de chat."""

import logging

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.chat_serializers import (
    AvaliarAberturaChatSerializer,
    CriarSessaoChatSerializer,
    InteragirChatSerializer,
    MensagemChatSerializer,
    SessaoChatSerializer,
)
from atendimentos.chat_estado import get_meta, set_meta
from atendimentos.chat_services import criar_sessao_com_boas_vindas, registrar_mensagem_cidadao
from atendimentos.models import MensagemChat, SessaoChat
from atendimentos.tasks import processar_mensagem_ia

logger = logging.getLogger(__name__)

IA_REPROCESSAR_APOS_SEG = 20


def _calcular_ia_processando(sessao: SessaoChat, mensagens) -> bool:
    ultima_ia = mensagens.filter(autor="ia").order_by("-criado_em").first()
    return (
        sessao.status == SessaoChat.Status.EM_ANDAMENTO
        and mensagens.filter(autor="cidadao").exists()
        and (
            not ultima_ia
            or mensagens.filter(autor="cidadao", criado_em__gt=ultima_ia.criado_em).exists()
        )
    )


def _reprocessar_turno_travado(sessao: SessaoChat, mensagens) -> None:
    """Reenfileira IA se o cidadão enviou mensagem e não há resposta há vários segundos."""
    ultima_cid = mensagens.filter(autor=MensagemChat.Autor.CIDADAO).order_by("-criado_em").first()
    if not ultima_cid:
        return
    idade_s = (timezone.now() - ultima_cid.criado_em).total_seconds()
    if idade_s < IA_REPROCESSAR_APOS_SEG:
        return
    cid_id = str(ultima_cid.id)
    if get_meta(sessao).get("ia_reprocess_cidadao_id") == cid_id:
        return
    logger.warning(
        "Reenfileirando turno IA travado (sessão=%s, mensagem_cidadao=%s, idade=%.0fs)",
        sessao.id,
        cid_id,
        idade_s,
    )
    processar_mensagem_ia.apply_async(
        args=[str(sessao.id), cid_id],
        kwargs={"confirmar_protocolo": False, "dados_slot": {}},
        queue="ouve",
    )
    set_meta(sessao, ia_reprocess_cidadao_id=cid_id)
    sessao.save(update_fields=["dados_coletados", "atualizado_em"])


class CriarSessaoChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CriarSessaoChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sessao, mensagem = criar_sessao_com_boas_vindas(
            request.user,
            serializer.validated_data["categoria_inicial"],
        )

        return Response(
            {
                "sessao": SessaoChatSerializer(sessao, context={"request": request}).data,
                "mensagem": MensagemChatSerializer(mensagem).data,
            },
            status=status.HTTP_201_CREATED,
        )


class InteragirChatView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = InteragirChatSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        sessao = serializer.context["sessao"]
        texto = serializer.validated_data.get("texto", "")
        loc = serializer.validated_data.get("localizacao") or {}
        confirmar_protocolo = bool(serializer.validated_data.get("confirmar_protocolo"))
        dados_slot = serializer.validated_data.get("dados_slot")

        arquivos = list(request.FILES.getlist("midia") or request.FILES.getlist("arquivos") or [])

        msg_cidadao, qtd_anexos = registrar_mensagem_cidadao(
            sessao,
            texto=texto,
            latitude=loc.get("latitude"),
            longitude=loc.get("longitude"),
            endereco=loc.get("endereco", ""),
            arquivos=arquivos,
        )

        task = processar_mensagem_ia.apply_async(
            args=[str(sessao.id), str(msg_cidadao.id)],
            kwargs={
                "confirmar_protocolo": confirmar_protocolo,
                "dados_slot": dados_slot or {},
            },
            queue="ouve",
        )

        sessao.refresh_from_db()

        return Response(
            {
                "status": "processando",
                "task_id": task.id,
                "sessao": SessaoChatSerializer(sessao, context={"request": request}).data,
                "mensagem_cidadao": MensagemChatSerializer(msg_cidadao).data,
                "midia_recebida": qtd_anexos,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class AvaliarAberturaChatView(APIView):
    """Pesquisa de satisfação com o processo de abertura (chat), distinta do CSAT de protocolo resolvido."""

    permission_classes = [IsAuthenticated]

    def post(self, request, sessao_id):
        sessao = get_object_or_404(SessaoChat, pk=sessao_id, usuario=request.user)
        serializer = AvaliarAberturaChatSerializer(
            data=request.data,
            context={"request": request, "sessao": sessao},
        )
        serializer.is_valid(raise_exception=True)
        sessao = serializer.save()
        return Response(
            {
                "nota": sessao.nota_abertura,
                "comentario": sessao.comentario_abertura or "",
                "protocolo_id": str(sessao.protocolo_final_id),
                "avaliacao_abertura_em": sessao.avaliacao_abertura_em.isoformat()
                if sessao.avaliacao_abertura_em
                else None,
            },
            status=status.HTTP_201_CREATED,
        )


class ListarMensagensChatView(APIView):
    """Polling: lista mensagens da sessão em ordem cronológica."""

    permission_classes = [IsAuthenticated]

    def get(self, request, sessao_id):
        sessao = get_object_or_404(SessaoChat, pk=sessao_id, usuario=request.user)
        mensagens = sessao.mensagens.order_by("criado_em")

        protocolo = None
        if sessao.protocolo_final_id:
            p = sessao.protocolo_final
            protocolo = {"codigo": p.codigo, "id": str(p.id)}

        ia_processando = _calcular_ia_processando(sessao, mensagens)
        if ia_processando:
            _reprocessar_turno_travado(sessao, mensagens)
            sessao.refresh_from_db(fields=["dados_coletados", "atualizado_em"])
            mensagens = sessao.mensagens.order_by("criado_em")
            ia_processando = _calcular_ia_processando(sessao, mensagens)

        return Response(
            {
                "sessao": SessaoChatSerializer(sessao, context={"request": request}).data,
                "mensagens": MensagemChatSerializer(mensagens, many=True).data,
                "protocolo": protocolo,
                "ia_processando": ia_processando,
            },
            status=status.HTTP_200_OK,
        )
