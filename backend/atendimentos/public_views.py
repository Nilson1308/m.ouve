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

from atendimentos.magic_link_context_service import (
    montar_contexto_magic_link,
    motivo_bloqueio_magic_link,
)
from atendimentos.models import AnexoOrdemServico, OrdemServico


def _carregar_ordem_por_token(token_magic_link) -> tuple[OrdemServico | None, Response | None]:
    try:
        token = uuid.UUID(str(token_magic_link).strip())
    except ValueError:
        return None, Response(
            {"detail": "Token inválido."},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        ordem = (
            OrdemServico.objects.select_related(
                "protocolo",
                "protocolo__servico",
                "protocolo__equipamento",
                "unidade",
            )
            .prefetch_related("anexos", "protocolo__anexos")
            .get(magic_link_token=token)
        )
    except OrdemServico.DoesNotExist:
        return None, Response(
            {"detail": "Link não encontrado."},
            status=status.HTTP_404_NOT_FOUND,
        )
    return ordem, None


class PublicoEvidenciasMagicLinkView(APIView):
    """
    GET — contexto operacional (LGPD, sem PII do cidadão).
  POST multipart — anexos da equipe de rua.
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, token_magic_link):
        ordem, err = _carregar_ordem_por_token(token_magic_link)
        if err:
            return err
        bloqueio = motivo_bloqueio_magic_link(ordem)
        if bloqueio:
            code, detail = bloqueio
            return Response({"detail": detail}, status=code)
        payload = montar_contexto_magic_link(ordem, request=request)
        return Response(payload, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, token_magic_link):
        ordem, err = _carregar_ordem_por_token(token_magic_link)
        if err:
            return err

        bloqueio = motivo_bloqueio_magic_link(ordem)
        if bloqueio:
            code, detail = bloqueio
            return Response({"detail": detail}, status=code)

        ordem = OrdemServico.objects.select_for_update().get(pk=ordem.pk)

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