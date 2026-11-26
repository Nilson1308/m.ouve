"""API — Copiloto analítico do gestor (Sprint 4.7B)."""

from __future__ import annotations

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.models import ConfiguracaoAgenteGestao, MensagemCopilotoGestor, SessaoCopilotoGestor
from atendimentos.services.agente_copiloto_service import (
    config_usuario_payload,
    contar_perguntas_hoje,
    criar_sessao_ou_reusar,
    montar_resposta_sessao,
    verificar_copiloto_disponivel,
)
from core_auth.permissions import IsBackofficeStaff


class CopilotoConfigUsuarioView(APIView):
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request):
        rota = (request.query_params.get("rota") or "").strip()
        return Response(config_usuario_payload(request.user, rota=rota))


class CopilotoPerguntarView(APIView):
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def post(self, request):
        cfg = ConfiguracaoAgenteGestao.load()
        ok, motivo = verificar_copiloto_disponivel(request.user)
        if not ok:
            return Response({"detail": motivo}, status=status.HTTP_403_FORBIDDEN)

        pergunta = (request.data.get("pergunta") or "").strip()
        if len(pergunta) < 3:
            return Response({"pergunta": "Mínimo 3 caracteres."}, status=status.HTTP_400_BAD_REQUEST)
        if len(pergunta) > 600:
            return Response({"pergunta": "Máximo 600 caracteres."}, status=status.HTTP_400_BAD_REQUEST)

        perguntas_hoje = contar_perguntas_hoje(request.user)
        limite = int(cfg.limite_perguntas_dia_por_usuario)
        if perguntas_hoje >= limite:
            return Response(
                {
                    "detail": "Limite diário de perguntas ao Copiloto atingido.",
                    "perguntas_hoje": perguntas_hoje,
                    "limite_diario": limite,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        sessao_id = (request.data.get("sessao_id") or "").strip() or None
        contexto_rota = (request.data.get("contexto_rota") or "").strip()[:120]

        try:
            sessao = criar_sessao_ou_reusar(
                request.user,
                pergunta,
                sessao_id=sessao_id,
                contexto_rota=contexto_rota,
            )
        except SessaoCopilotoGestor.DoesNotExist:
            return Response({"sessao_id": "Sessão não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            MensagemCopilotoGestor.objects.create(
                sessao=sessao,
                papel=MensagemCopilotoGestor.Papel.USUARIO,
                conteudo=pergunta,
                status_processamento=MensagemCopilotoGestor.StatusProcessamento.CONCLUIDA,
            )
            msg_assist = MensagemCopilotoGestor.objects.create(
                sessao=sessao,
                papel=MensagemCopilotoGestor.Papel.ASSISTENTE,
                conteudo="",
                status_processamento=MensagemCopilotoGestor.StatusProcessamento.PROCESSANDO,
            )
            assist_id = str(msg_assist.id)

            def _enfileirar():
                from atendimentos.tasks import processar_pergunta_copiloto_task

                processar_pergunta_copiloto_task.delay(assist_id)

            transaction.on_commit(_enfileirar)

        return Response(
            {
                "sessao_id": str(sessao.id),
                "mensagem_assistente_id": assist_id,
                "status": "processando",
                "perguntas_hoje": perguntas_hoje + 1,
                "limite_diario": limite,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class CopilotoSessoesListView(APIView):
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request):
        qs = SessaoCopilotoGestor.objects.filter(usuario=request.user).order_by("-atualizado_em")[:20]
        itens = [
            {
                "id": str(s.id),
                "titulo": s.titulo,
                "perspectiva": s.perspectiva,
                "unidade_id": str(s.unidade_id) if s.unidade_id else None,
                "contexto_rota_inicial": s.contexto_rota_inicial,
                "criado_em": s.criado_em.isoformat(),
                "atualizado_em": s.atualizado_em.isoformat(),
            }
            for s in qs
        ]
        return Response({"sessoes": itens})


class CopilotoSessaoDetalheView(APIView):
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request, sessao_id):
        sessao = get_object_or_404(SessaoCopilotoGestor, pk=sessao_id)
        if sessao.usuario_id != request.user.id:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(montar_resposta_sessao(sessao))

    def delete(self, request, sessao_id):
        sessao = get_object_or_404(SessaoCopilotoGestor, pk=sessao_id)
        if sessao.usuario_id != request.user.id:
            return Response(status=status.HTTP_404_NOT_FOUND)
        sessao.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)