"""API Backoffice — Super OS (incidente mestre) e sugestões de cluster."""

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.backoffice_serializers import (
    BackofficeOrdemServicoSerializer,
    DespacharProtocoloSerializer,
)
from atendimentos.backoffice_views import IsBackofficeStaff
from atendimentos.cluster_services import (
    DEFAULT_RAIO_METROS,
    dias_janela_cluster_ia,
    gerar_sugestoes_super_os,
)
from django.db.models import Count, Prefetch

from atendimentos.models import OrdemServico, Protocolo, ProtocoloHistorico, SuperOS
from atendimentos.super_os_serializers import (
    AgruparMapaSuperOSSerializer,
    AnexarProtocoloSuperOSSerializer,
    CriarRetroativaSuperOSSerializer,
    SuperOSDetalheSerializer,
    SuperOSSerializer,
)
from atendimentos.super_os_services import (
    anexar_protocolo_a_super_os,
    criar_super_os_a_partir_protocolos,
    criar_super_os_retroativa,
    despachar_super_os,
    integrar_ancora_operacional_super_os,
    super_os_precisa_integracao_ancora,
)


class SuperOSSugestoesView(APIView):
    """GET — clusters sugeridos por proximidade geográfica e tipo de serviço."""

    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request):
        try:
            raio = float(request.query_params.get("raio_metros", DEFAULT_RAIO_METROS))
        except (TypeError, ValueError):
            raio = DEFAULT_RAIO_METROS
        raio = max(50.0, min(raio, 5000.0))

        try:
            min_protocolos = int(request.query_params.get("min_protocolos", 2))
        except (TypeError, ValueError):
            min_protocolos = 2
        min_protocolos = max(2, min(min_protocolos, 50))

        sugestoes = gerar_sugestoes_super_os(
            raio_metros=raio,
            min_protocolos=min_protocolos,
        )
        return Response(
            {
                "raio_metros": raio,
                "min_protocolos": min_protocolos,
                "dias_busca_cluster_ia": dias_janela_cluster_ia(),
                "sugestoes": sugestoes,
                "count": len(sugestoes),
            }
        )


def queryset_super_os_detalhe():
    historico_qs = ProtocoloHistorico.objects.order_by("registrado_em")
    filhos_qs = (
        Protocolo.objects.select_related("usuario", "servico", "servico__categoria", "sessao_chat")
        .prefetch_related(Prefetch("historico", queryset=historico_qs))
        .order_by("data_criacao")
    )
    return SuperOS.objects.prefetch_related(
        Prefetch("protocolos_filhos", queryset=filhos_qs),
        Prefetch("ordens_servico", queryset=OrdemServico.objects.select_related("unidade")),
    ).annotate(qtd_filhos=Count("protocolos_filhos", distinct=True))


class SuperOSDetalheView(APIView):
    """GET — dossiê profundo (filhos, chat, dados coletados, centroide)."""

    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request, super_os_id):
        super_os = get_object_or_404(queryset_super_os_detalhe(), pk=super_os_id)
        super_os._quantidade_filhos = super_os.qtd_filhos
        data = SuperOSDetalheSerializer(super_os, context={"request": request}).data
        return Response(data)


class SuperOSRetroativaView(APIView):
    """POST — Super OS retroativa em torno de protocolo âncora (OS já no setorial)."""

    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    @transaction.atomic
    def post(self, request):
        serializer = CriarRetroativaSuperOSSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            super_os = criar_super_os_retroativa(
                protocolo_ancora_id=str(data["protocolo_ancora_id"]),
                protocolos_novos_ids=[str(uid) for uid in data["protocolos_ids"]],
                titulo_resumo=data["titulo_resumo"],
                descricao_geral=data.get("descricao_geral") or "",
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        ids_filhos = [
            str(pk) for pk in super_os.protocolos_filhos.values_list("pk", flat=True)
        ]
        super_os._prefetched_filhos_ids = ids_filhos
        super_os._quantidade_filhos = len(ids_filhos)

        return Response(
            {
                "sucesso": True,
                "super_os": SuperOSSerializer(super_os).data,
                "protocolo_ancora_id": str(data["protocolo_ancora_id"]),
                "quantidade_protocolos": len(ids_filhos),
            },
            status=status.HTTP_201_CREATED,
        )


class SuperOSAgruparMapaView(APIView):
    """POST — cria Super OS a partir de protocolos selecionados no mapa."""

    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def post(self, request):
        serializer = AgruparMapaSuperOSSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            super_os = criar_super_os_a_partir_protocolos(
                protocolos_ids=[str(uid) for uid in data["protocolos_ids"]],
                titulo_resumo=data["titulo_resumo"],
                descricao_geral=data.get("descricao_geral") or "",
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        super_os._prefetched_filhos_ids = [str(uid) for uid in data["protocolos_ids"]]
        super_os._quantidade_filhos = len(data["protocolos_ids"])

        return Response(
            {
                "sucesso": True,
                "super_os": SuperOSSerializer(super_os).data,
            },
            status=status.HTTP_201_CREATED,
        )


class SuperOSIntegrarAncoraView(APIView):
    """POST — vincula OS já existente no setorial ao incidente mestre (correção/retroativa)."""

    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    @transaction.atomic
    def post(self, request, super_os_id):
        super_os = get_object_or_404(
            SuperOS.objects.select_for_update().prefetch_related(
                "protocolos_filhos__ordens_servico",
                "ordens_servico",
            ),
            pk=super_os_id,
        )
        try:
            super_os = integrar_ancora_operacional_super_os(super_os)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        super_os._prefetched_filhos_ids = [
            str(pk) for pk in super_os.protocolos_filhos.values_list("pk", flat=True)
        ]
        super_os._quantidade_filhos = len(super_os._prefetched_filhos_ids)

        return Response(
            {
                "sucesso": True,
                "super_os": SuperOSSerializer(super_os).data,
                "precisa_integracao_ancora": super_os_precisa_integracao_ancora(
                    super_os
                ),
            },
            status=status.HTTP_200_OK,
        )


class SuperOSAnexarView(APIView):
    """POST — anexa protocolo a Super OS existente (bypass de despacho individual)."""

    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    @transaction.atomic
    def post(self, request, super_os_id):
        super_os = get_object_or_404(
            SuperOS.objects.select_for_update(),
            pk=super_os_id,
        )
        serializer = AnexarProtocoloSuperOSSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        protocolo_id = str(serializer.validated_data["protocolo_id"])
        try:
            protocolo = anexar_protocolo_a_super_os(super_os, protocolo_id)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        super_os.refresh_from_db()
        super_os._prefetched_filhos_ids = [
            str(pk) for pk in super_os.protocolos_filhos.values_list("pk", flat=True)
        ]
        super_os._quantidade_filhos = len(super_os._prefetched_filhos_ids)

        return Response(
            {
                "sucesso": True,
                "super_os": SuperOSSerializer(super_os).data,
                "protocolo": {
                    "id": str(protocolo.id),
                    "codigo": protocolo.codigo,
                    "status": protocolo.status,
                    "super_os_id": str(super_os.id),
                },
            },
            status=status.HTTP_200_OK,
        )


class SuperOSDespacharView(APIView):
    """POST — scatter-gather da Super OS para uma ou mais unidades."""

    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    @transaction.atomic
    def post(self, request, super_os_id):
        super_os = get_object_or_404(
            SuperOS.objects.select_for_update().prefetch_related("protocolos_filhos"),
            pk=super_os_id,
        )
        serializer = DespacharProtocoloSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            super_os, ordens_criadas = despachar_super_os(
                super_os,
                data["ordens"],
                observacao_geral=data.get("observacao_geral") or "",
                despachado_por=request.user,
                request=request,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        super_os.refresh_from_db()
        super_os._prefetched_filhos_ids = [
            str(pk) for pk in super_os.protocolos_filhos.values_list("pk", flat=True)
        ]
        super_os._quantidade_filhos = len(super_os._prefetched_filhos_ids)

        return Response(
            {
                "super_os": SuperOSSerializer(super_os).data,
                "ordens_servico": BackofficeOrdemServicoSerializer(
                    ordens_criadas, many=True, context={"request": request}
                ).data,
                "despachado_em": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "quantidade_protocolos_filhos": super_os._quantidade_filhos,
            },
            status=status.HTTP_201_CREATED,
        )