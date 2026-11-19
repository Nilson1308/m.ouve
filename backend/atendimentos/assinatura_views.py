"""APIs de solicitação e assinatura eletrônica hierárquica."""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.assinatura_serializers import (
    AssinarDespachoSerializer,
    RejeitarAssinaturaSerializer,
    SolicitacaoAssinaturaPendenteSerializer,
    SolicitacaoAssinaturaSerializer,
    SolicitarAssinaturaSerializer,
)
from atendimentos.assinatura_services import (
    gerar_hash_assinatura_hierarquica,
    resolver_assinante_destino,
)
from atendimentos.backoffice_services import (
    concluir_atendimento_setor,
    marcar_ordem_concluida,
)
from atendimentos.models import (
    AnexoOrdemServico,
    OrdemServico,
    Protocolo,
    ProtocoloHistorico,
    SolicitacaoAssinatura,
)
from atendimentos.notificacoes_internas import notificar_os_formalizada_ouvidor
from atendimentos.servicos_notificacao import criar_notificacao_interna
from atendimentos.backoffice_views import IsBackofficeStaff
from atendimentos.setorial_views import IsSetorialStaff, usuario_pode_gerir_ordem
from core_auth.display import nome_servidor
from ouvia_core.url_utils import public_absolute_uri

User = get_user_model()


def _usuario_pode_assinar(user, solicitacao) -> bool:
    if not user or not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False):
        return True
    return str(solicitacao.assinante_destino_id) == str(user.pk)


def _erro_contrato(code: str, message: str, *, status_code=status.HTTP_400_BAD_REQUEST, details=None):
    return Response(
        {
            "error": {
                "code": code,
                "message": message,
                "details": details,
            }
        },
        status=status_code,
    )


def _link_setorial(request) -> str:
    path = "/backoffice/setorial"
    return public_absolute_uri(request, path) or path


def queryset_assinaturas_pendentes_usuario(user):
    filtro = {"status": SolicitacaoAssinatura.Status.PENDENTE}
    if not getattr(user, "is_superuser", False):
        filtro["assinante_destino"] = user
    return (
        SolicitacaoAssinatura.objects.filter(**filtro)
        .select_related(
            "solicitante",
            "assinante_destino",
            "ordem_servico",
            "ordem_servico__protocolo",
            "ordem_servico__protocolo__servico",
            "ordem_servico__unidade",
            "ordem_servico__formalizado_por",
        )
        .prefetch_related(
            Prefetch(
                "ordem_servico__anexos",
                queryset=AnexoOrdemServico.objects.order_by("criado_em"),
            )
        )
        .order_by("-criado_em")
    )


class AssinantesElegiveisListView(APIView):
    """Servidores staff da mesma unidade (exceto o usuário logado) para designar assinatura."""

    permission_classes = [IsAuthenticated, IsSetorialStaff]

    def get(self, request):
        qs = User.objects.filter(is_staff=True, is_active=True).exclude(pk=request.user.pk)
        if not getattr(request.user, "is_superuser", False):
            if not request.user.unidade_id:
                return Response({"results": [], "count": 0})
            qs = qs.filter(unidade_id=request.user.unidade_id)
        qs = qs.order_by("nome")
        results = [
            {
                "id": str(u.pk),
                "nome": u.nome or u.email,
                "email": u.email,
            }
            for u in qs[:100]
        ]
        return Response({"results": results, "count": len(results)})


class AssinaturasPendentesListView(APIView):
    """Lista solicitações pendentes em que o usuário logado é o assinante."""

    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request):
        qs = queryset_assinaturas_pendentes_usuario(request.user)
        data = SolicitacaoAssinaturaPendenteSerializer(
            qs, many=True, context={"request": request}
        ).data
        return Response(
            {
                "results": data,
                "count": len(data),
            }
        )


class SolicitarAssinaturaView(APIView):
    """Operador elabora despacho e encaminha ao superior para assinatura."""

    permission_classes = [IsAuthenticated, IsSetorialStaff]

    @transaction.atomic
    def post(self, request):
        serializer = SolicitarAssinaturaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        ordem = get_object_or_404(
            OrdemServico.objects.select_for_update().select_related(
                "protocolo", "unidade"
            ),
            pk=data["ordem_servico_id"],
        )
        if not usuario_pode_gerir_ordem(request.user, ordem):
            return Response(
                {"detail": "Ordem não pertence à sua unidade administrativa."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if ordem.status in (
            OrdemServico.Status.CONCLUIDA,
            OrdemServico.Status.CANCELADA,
        ):
            return Response(
                {"detail": "Ordem encerrada não aceita nova solicitação de assinatura."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if ordem.status == OrdemServico.Status.AGUARDANDO_ASSINATURA:
            pendente = (
                SolicitacaoAssinatura.objects.filter(
                    ordem_servico=ordem,
                    status=SolicitacaoAssinatura.Status.PENDENTE,
                )
                .select_related("assinante_destino")
                .order_by("-criado_em")
                .first()
            )
            if pendente:
                assinante = pendente.assinante_destino
                return Response(
                    {
                        "sucesso": True,
                        "already_pending": True,
                        "detail": (
                            "Despacho já encaminhado. Aguardando assinatura do gestor."
                        ),
                        "solicitacao_assinatura": SolicitacaoAssinaturaSerializer(
                            pendente
                        ).data,
                        "assinante_destino_nome": assinante.nome or assinante.email,
                        "ordem_servico_status": ordem.status,
                    },
                    status=status.HTTP_200_OK,
                )

        assinante_id = data.get("assinante_destino_id")
        if assinante_id:
            if assinante_id == request.user.pk:
                return Response(
                    {"detail": "O assinante deve ser diferente do solicitante."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            assinante = get_object_or_404(
                User.objects.filter(is_staff=True, is_active=True),
                pk=assinante_id,
            )
        else:
            assinante = resolver_assinante_destino(request.user, ordem)
            if not assinante:
                return Response(
                    {
                        "detail": (
                            "Não há gestor disponível para assinatura nesta unidade. "
                            "Cadastre um servidor gestor na secretaria ou na Mesa da Ouvidoria "
                            "(conta staff sem unidade setorial)."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        solicitacao = SolicitacaoAssinatura.objects.create(
            ordem_servico=ordem,
            solicitante=request.user,
            assinante_destino=assinante,
            despacho_tecnico=data["despacho_tecnico"],
        )
        ordem.despacho_tecnico = data["despacho_tecnico"]
        ordem.status = OrdemServico.Status.AGUARDANDO_ASSINATURA
        ordem.save(update_fields=["despacho_tecnico", "status", "atualizado_em"])

        codigo = ordem.protocolo.codigo if ordem.protocolo_id else str(ordem.pk)[:8]
        criar_notificacao_interna(
            assinante.pk,
            f"Assinatura solicitada — OS {codigo}",
            (
                f"{nome_servidor(request.user)} solicitou sua "
                f"assinatura eletrônica no despacho da ordem vinculada ao protocolo {codigo}."
            ),
            link_acao=_link_setorial(request),
        )

        return Response(
            {
                "sucesso": True,
                "solicitacao_assinatura": SolicitacaoAssinaturaSerializer(
                    solicitacao
                ).data,
                "assinante_destino_nome": assinante.nome or assinante.email,
                "ordem_servico_status": ordem.status,
            },
            status=status.HTTP_201_CREATED,
        )


class AssinarSolicitacaoView(APIView):
    """Superior assina o despacho com senha (hash SHA-256)."""

    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    @transaction.atomic
    def post(self, request, solicitacao_id):
        solicitacao = get_object_or_404(
            SolicitacaoAssinatura.objects.select_for_update()
            .select_related(
                "ordem_servico",
                "ordem_servico__protocolo",
                "ordem_servico__unidade",
                "solicitante",
                "assinante_destino",
            ),
            pk=solicitacao_id,
        )

        if not _usuario_pode_assinar(request.user, solicitacao):
            destino = solicitacao.assinante_destino
            nome_destino = nome_servidor(destino) if destino else "o gestor designado"
            return _erro_contrato(
                "ASSINANTE_NAO_AUTORIZADO",
                (
                    f"Somente {nome_destino} pode assinar esta solicitação. "
                    "Acesse a Mesa com a conta do gestor indicado ou peça uma nova solicitação."
                ),
                status_code=status.HTTP_403_FORBIDDEN,
                details={
                    "assinante_destino_id": str(solicitacao.assinante_destino_id),
                    "assinante_destino_nome": nome_destino,
                },
            )
        if solicitacao.status != SolicitacaoAssinatura.Status.PENDENTE:
            return Response(
                {"detail": f"Solicitação já está {solicitacao.get_status_display().lower()}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AssinarDespachoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(serializer.validated_data["senha_assinatura"]):
            return _erro_contrato(
                "SENHA_ASSINATURA_INVALIDA",
                "Senha incorreta. Use a mesma senha do seu login institucional.",
            )

        ordem = OrdemServico.objects.select_for_update().get(
            pk=solicitacao.ordem_servico_id
        )
        if ordem.status != OrdemServico.Status.AGUARDANDO_ASSINATURA:
            return Response(
                {"detail": "A ordem não está aguardando assinatura."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        digest, momento = gerar_hash_assinatura_hierarquica(
            request.user.pk,
            solicitacao.despacho_tecnico,
        )

        solicitacao.status = SolicitacaoAssinatura.Status.ASSINADA
        solicitacao.hash_assinatura = digest
        solicitacao.assinada_em = momento
        solicitacao.save(
            update_fields=["status", "hash_assinatura", "assinada_em", "atualizado_em"]
        )

        marcar_ordem_concluida(
            ordem,
            despacho_tecnico=solicitacao.despacho_tecnico,
            formalizado_por=request.user,
            assinatura_hash=digest,
            data_formalizacao=momento,
        )

        protocolo = Protocolo.objects.select_for_update().get(pk=ordem.protocolo_id)
        unidade = ordem.unidade
        unidade_label = unidade.sigla or unidade.nome if unidade else "Secretaria"
        ProtocoloHistorico.objects.create(
            protocolo=protocolo,
            status=protocolo.status,
            descricao=(
                f"Ordem formalizada com assinatura hierárquica — {unidade_label}. "
                f"Hash: {digest[:12]}…"
            ),
            equipe_nome=getattr(request.user, "nome", "") or "",
        )
        concluir_atendimento_setor(
            protocolo,
            ordem,
            despacho_tecnico=solicitacao.despacho_tecnico,
            equipe_nome=unidade_label,
            unidade_nome=unidade_label,
        )
        notificar_os_formalizada_ouvidor(ordem, request=request)

        criar_notificacao_interna(
            solicitacao.solicitante_id,
            f"Despacho assinado — {protocolo.codigo}",
            (
                f"Sua solicitação de assinatura foi concluída por "
                f"{nome_servidor(request.user)}. "
                f"A ordem de serviço foi encerrada."
            ),
            link_acao=_link_setorial(request),
        )

        solicitacao.refresh_from_db()
        ordem.refresh_from_db()
        protocolo.refresh_from_db()

        return Response(
            {
                "sucesso": True,
                "solicitacao_assinatura": SolicitacaoAssinaturaSerializer(
                    solicitacao
                ).data,
                "hash_assinatura": digest,
                "ordem_servico_status": ordem.status,
                "protocolo_status": protocolo.status,
            },
            status=status.HTTP_200_OK,
        )


class RejeitarSolicitacaoView(APIView):
    """Assinante recusa o despacho; OS volta a aguardando formalização."""

    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    @transaction.atomic
    def post(self, request, solicitacao_id):
        solicitacao = get_object_or_404(
            SolicitacaoAssinatura.objects.select_for_update()
            .select_related(
                "ordem_servico",
                "ordem_servico__protocolo",
                "solicitante",
                "assinante_destino",
            ),
            pk=solicitacao_id,
        )

        if not _usuario_pode_assinar(request.user, solicitacao):
            destino = solicitacao.assinante_destino
            nome_destino = nome_servidor(destino) if destino else "o gestor designado"
            return _erro_contrato(
                "ASSINANTE_NAO_AUTORIZADO",
                f"Somente {nome_destino} pode rejeitar esta solicitação.",
                status_code=status.HTTP_403_FORBIDDEN,
                details={"assinante_destino_nome": nome_destino},
            )
        if solicitacao.status != SolicitacaoAssinatura.Status.PENDENTE:
            return Response(
                {"detail": f"Solicitação já está {solicitacao.get_status_display().lower()}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RejeitarAssinaturaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        motivo = serializer.validated_data["motivo_rejeicao"]

        ordem = OrdemServico.objects.select_for_update().get(
            pk=solicitacao.ordem_servico_id
        )
        if ordem.status != OrdemServico.Status.AGUARDANDO_ASSINATURA:
            return Response(
                {"detail": "A ordem não está aguardando assinatura."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        momento = timezone.now()
        solicitacao.status = SolicitacaoAssinatura.Status.REJEITADA
        solicitacao.motivo_rejeicao = motivo
        solicitacao.rejeitada_em = momento
        solicitacao.save(
            update_fields=[
                "status",
                "motivo_rejeicao",
                "rejeitada_em",
                "atualizado_em",
            ]
        )

        ordem.status = OrdemServico.Status.AGUARDANDO_FORMALIZACAO
        ordem.save(update_fields=["status", "atualizado_em"])

        protocolo = ordem.protocolo
        codigo = protocolo.codigo if protocolo else str(ordem.pk)[:8]
        assinante_nome = (
            nome_servidor(request.user) or "Assinante"
        )
        criar_notificacao_interna(
            solicitacao.solicitante_id,
            f"Assinatura rejeitada — {codigo}",
            (
                f"{assinante_nome} rejeitou sua solicitação de assinatura "
                f"no protocolo {codigo}. Motivo: {motivo}"
            ),
            link_acao=_link_setorial(request),
        )

        solicitacao.refresh_from_db()
        ordem.refresh_from_db()

        return Response(
            {
                "sucesso": True,
                "solicitacao_assinatura": SolicitacaoAssinaturaSerializer(
                    solicitacao
                ).data,
                "ordem_servico_status": ordem.status,
            },
            status=status.HTTP_200_OK,
        )