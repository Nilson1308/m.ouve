"""Endpoints públicos (sem JWT) — upload de evidências via link mágico."""

import mimetypes
import uuid

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.magic_link_services import token_magic_link_valido
from atendimentos.models import AnexoOrdemServico, OrdemServico


class PublicoEvidenciasMagicLinkView(APIView):
    """
    POST multipart — anexos da equipe de rua.
    Não expõe dados do cidadão na resposta.
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser]

    @transaction.atomic
    def post(self, request, token_magic_link):
        try:
            token = uuid.UUID(str(token_magic_link).strip())
        except ValueError:
            return Response(
                {"detail": "Token inválido."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            ordem = OrdemServico.objects.select_for_update().get(magic_link_token=token)
        except OrdemServico.DoesNotExist:
            return Response(
                {"detail": "Link não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if ordem.status == OrdemServico.Status.CANCELADA:
            return Response(
                {"detail": "Esta ordem não aceita evidências."},
                status=status.HTTP_410_GONE,
            )
        if ordem.status == OrdemServico.Status.CONCLUIDA:
            return Response(
                {"detail": "Ordem já concluída — envio de evidências encerrado."},
                status=status.HTTP_410_GONE,
            )

        if not token_magic_link_valido(ordem):
            return Response(
                {"detail": "Link expirado. Solicite um novo link à secretaria."},
                status=status.HTTP_410_GONE,
            )

        arquivos = (
            request.FILES.getlist("anexos")
            or request.FILES.getlist("arquivos")
            or request.FILES.getlist("midia")
        )
        descricao = (request.data.get("descricao") or "").strip()
        audio_arquivos = (
            request.FILES.getlist("audio")
            or request.FILES.getlist("audios")
            or []
        )

        if not arquivos and not audio_arquivos:
            return Response(
                {"detail": "Envie ao menos uma foto ou um áudio de evidência."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if descricao:
            trecho = f"[Equipe de campo — {timezone.now().strftime('%d/%m/%Y %H:%M')}] {descricao}"
            if ordem.observacoes_execucao:
                ordem.observacoes_execucao = f"{ordem.observacoes_execucao.strip()}\n\n{trecho}"
            else:
                ordem.observacoes_execucao = trecho

        tipos_raw = request.data.getlist("tipo_evidencia")
        criados = 0
        for idx, arquivo in enumerate(arquivos):
            tipo_ev = (
                tipos_raw[idx].strip()
                if idx < len(tipos_raw) and tipos_raw[idx]
                else AnexoOrdemServico.TipoEvidencia.DEPOIS
            )
            if tipo_ev not in dict(AnexoOrdemServico.TipoEvidencia.choices):
                tipo_ev = AnexoOrdemServico.TipoEvidencia.DEPOIS
            guessed, _ = mimetypes.guess_type(arquivo.name)
            AnexoOrdemServico.objects.create(
                ordem=ordem,
                arquivo=arquivo,
                nome_original=arquivo.name,
                tipo_mime=guessed or getattr(arquivo, "content_type", "") or "",
                tipo_evidencia=tipo_ev,
            )
            criados += 1

        for audio in audio_arquivos:
            guessed, _ = mimetypes.guess_type(audio.name)
            tipo_mime = guessed or getattr(audio, "content_type", "") or "audio/webm"
            AnexoOrdemServico.objects.create(
                ordem=ordem,
                arquivo=audio,
                nome_original=audio.name or "relato-audio.webm",
                tipo_mime=tipo_mime,
                tipo_evidencia=AnexoOrdemServico.TipoEvidencia.OUTRO,
            )
            criados += 1

        ordem.magic_link_acessos = (ordem.magic_link_acessos or 0) + 1
        if ordem.status in (
            OrdemServico.Status.PENDENTE,
            OrdemServico.Status.EM_ANDAMENTO,
        ):
            ordem.status = OrdemServico.Status.AGUARDANDO_FORMALIZACAO
        update_fields = ["magic_link_acessos", "status", "atualizado_em"]
        if descricao:
            update_fields.append("observacoes_execucao")
        ordem.save(update_fields=update_fields)

        return Response(
            {
                "sucesso": True,
                "anexos_recebidos": criados,
                "status": ordem.status,
                "mensagem": "Evidências enviadas com sucesso.",
            },
            status=status.HTTP_201_CREATED,
        )
