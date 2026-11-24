"""APIs do painel setorial (gestor da unidade administrativa)."""

import mimetypes
import uuid

from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.backoffice_services import (
    ProtocoloEncerradoError,
    concluir_atendimento_setor,
    garantir_protocolo_tramitavel,
    marcar_ordem_concluida as concluir_os,
)
from atendimentos.magic_link_services import (
    build_magic_link_url,
    gerar_magic_link_ordem,
    magic_link_payload,
    registrar_assinatura_hash,
)
from atendimentos.models import (
    AnexoOrdemServico,
    DiligenciaProtocolo,
    OrdemServico,
    Protocolo,
    ProtocoloHistorico,
)
from atendimentos.notificacoes_internas import notificar_os_formalizada_ouvidor
from atendimentos.setorial_serializers import (
    FormalizarOrdemSerializer,
    SetorialOrdemServicoResumoSerializer,
    SetorialOrdemServicoSerializer,
)
from core_auth.permissions import IsSetorialStaff


STATUS_UI_PARA_ORDEM = {
    "nova": [OrdemServico.Status.PENDENTE],
    "aguardando_campo": [
        OrdemServico.Status.EM_ANDAMENTO,
        OrdemServico.Status.AGUARDANDO_FORMALIZACAO,
    ],
    "aguardando_assinatura": [OrdemServico.Status.AGUARDANDO_ASSINATURA],
    "concluida": [OrdemServico.Status.CONCLUIDA],
}


class SetorialOrdemFilterSet(filters.FilterSet):
    busca = filters.CharFilter(method="filter_busca")
    servico_id = filters.BaseInFilter(field_name="protocolo__servico_id")
    bairro = filters.BaseInFilter(method="filter_bairro")
    status_ui = filters.BaseInFilter(method="filter_status_ui")
    urgencia = filters.BaseInFilter(method="filter_urgencia")
    apenas_reabertos = filters.BooleanFilter(method="filter_apenas_reabertos")

    class Meta:
        model = OrdemServico
        fields = ()

    def filter_busca(self, queryset, name, value):
        if not value:
            return queryset
        termo = value.strip()
        if not termo:
            return queryset
        return queryset.filter(
            Q(descricao__icontains=termo)
            | Q(protocolo__codigo__icontains=termo)
            | Q(protocolo__descricao__icontains=termo)
            | Q(protocolo__endereco_texto__icontains=termo)
        ).distinct()

    def filter_bairro(self, queryset, name, value):
        valores = value if isinstance(value, (list, tuple)) else [value]
        valores = [str(v).strip() for v in valores if str(v).strip()]
        if not valores:
            return queryset
        q = Q()
        for bairro in valores:
            q |= Q(protocolo__dados_dinamicos__bairro__iexact=bairro) | Q(
                protocolo__dados_dinamicos__bairro__icontains=bairro
            )
        return queryset.filter(q).distinct()

    def filter_status_ui(self, queryset, name, value):
        valores = value if isinstance(value, (list, tuple)) else [value]
        valores = [str(v).strip() for v in valores if str(v).strip()]
        if not valores:
            return queryset
        status_api = []
        for ui in valores:
            status_api.extend(STATUS_UI_PARA_ORDEM.get(ui, []))
        if not status_api:
            return queryset.none()
        return queryset.filter(status__in=status_api).distinct()

    def filter_urgencia(self, queryset, name, value):
        valores = value if isinstance(value, (list, tuple)) else [value]
        valores = [str(v).strip().lower() for v in valores if str(v).strip()]
        if not valores:
            return queryset
        q = Q()
        for val in valores:
            q |= (
                Q(protocolo__dados_dinamicos__urgencia__iexact=val)
                | Q(protocolo__dados_dinamicos__prioridade__iexact=val)
                | Q(protocolo__dados_dinamicos__urgencia_estimada__iexact=val)
            )
        return queryset.filter(q).distinct()

    def filter_apenas_reabertos(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(protocolo__qtd_reaberturas__gte=1)


class SetorialFiltrosOpcoesView(APIView):
    """Opções de filtros avançados do painel setorial (escopo da unidade)."""

    permission_classes = [IsAuthenticated, IsSetorialStaff]

    def get(self, request):
        from catalogo.models import ServicoCatalogo

        qs = queryset_ordem_setorial(request.user)
        protocolo_ids = qs.values_list("protocolo_id", flat=True)

        bairros_set = set()
        for dados in Protocolo.objects.filter(pk__in=protocolo_ids).values_list(
            "dados_dinamicos", flat=True
        ):
            if not isinstance(dados, dict):
                continue
            bairro = (dados.get("bairro") or "").strip()
            if bairro:
                bairros_set.add(bairro)

        servico_ids = qs.values_list("protocolo__servico_id", flat=True).distinct()
        servicos = [
            {"id": str(s.id), "nome": s.nome}
            for s in ServicoCatalogo.objects.filter(pk__in=servico_ids).order_by("nome")
        ]

        return Response(
            {
                "bairros": sorted(bairros_set, key=lambda x: x.lower()),
                "servicos": servicos,
                "status": [
                    {"value": "nova", "label": "Nova"},
                    {"value": "aguardando_campo", "label": "Aguardando campo"},
                    {"value": "aguardando_assinatura", "label": "Aguardando gestor"},
                    {"value": "concluida", "label": "Concluída"},
                ],
                "urgencias": [
                    {"value": "baixa", "label": "Baixa"},
                    {"value": "normal", "label": "Normal"},
                    {"value": "media", "label": "Média"},
                    {"value": "alta", "label": "Alta"},
                    {"value": "critica", "label": "Crítica"},
                    {"value": "urgente", "label": "Urgente"},
                ],
            }
        )


def queryset_ordem_setorial(user):
    qs = (
        OrdemServico.objects.select_related(
            "protocolo",
            "protocolo__servico",
            "protocolo__usuario",
            "super_os",
            "unidade",
            "formalizado_por",
        )
        .annotate(
            super_os_qtd_filhos=Count(
                "super_os__protocolos_filhos",
                distinct=True,
            )
        )
        .prefetch_related(
            Prefetch("anexos", queryset=AnexoOrdemServico.objects.order_by("criado_em")),
            Prefetch(
                "protocolo__diligencias",
                queryset=DiligenciaProtocolo.objects.select_related(
                    "unidade_solicitante", "autor_servidor"
                ).order_by("-criado_em"),
            ),
        )
        .exclude(status=OrdemServico.Status.CANCELADA)
        .order_by("-criado_em")
    )
    if getattr(user, "is_superuser", False) and not user.unidade_id:
        return qs
    if not user.unidade_id:
        return qs.none()
    return qs.filter(unidade_id=user.unidade_id)


def usuario_pode_gerir_ordem(user, ordem: OrdemServico) -> bool:
    if getattr(user, "is_superuser", False):
        return True
    return bool(user.unidade_id and ordem.unidade_id == user.unidade_id)


class SetorialOrdensListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsSetorialStaff]
    serializer_class = SetorialOrdemServicoResumoSerializer
    pagination_class = None
    filterset_class = SetorialOrdemFilterSet

    def get_queryset(self):
        return queryset_ordem_setorial(self.request.user)


class SetorialOrdemDetalheView(APIView):
    """GET — detalhe de OS da unidade (diligências com anexos resolvidos)."""

    permission_classes = [IsAuthenticated, IsSetorialStaff]

    def get(self, request, ordem_id):
        ordem = get_object_or_404(queryset_ordem_setorial(request.user), pk=ordem_id)
        return Response(
            SetorialOrdemServicoSerializer(ordem, context={"request": request}).data
        )


class GerarMagicLinkOrdemView(APIView):
    permission_classes = [IsAuthenticated, IsSetorialStaff]

    @transaction.atomic
    def post(self, request, ordem_id):
        ordem = get_object_or_404(
            OrdemServico.objects.select_for_update().select_related("unidade", "protocolo"),
            pk=ordem_id,
        )
        if not usuario_pode_gerir_ordem(request.user, ordem):
            return Response(
                {"detail": "Ordem não pertence à sua unidade administrativa."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if ordem.status == OrdemServico.Status.CONCLUIDA:
            return Response(
                {"detail": "Ordem já concluída — link mágico não aplicável."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = gerar_magic_link_ordem(ordem)
        ordem.refresh_from_db()

        payload_link = magic_link_payload(ordem)
        return Response(
            {
                "magic_link": payload_link,
                "url": build_magic_link_url(token),
                "ordem_servico": SetorialOrdemServicoSerializer(
                    ordem, context={"request": request}
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )


class UploadEvidenciasOrdemSetorialView(APIView):
    """Upload autenticado de evidências (gestor setorial / backup ao link mágico)."""

    permission_classes = [IsAuthenticated, IsSetorialStaff]
    parser_classes = [MultiPartParser, FormParser]

    @transaction.atomic
    def post(self, request, ordem_id):
        ordem = get_object_or_404(
            OrdemServico.objects.select_for_update().select_related("unidade", "protocolo"),
            pk=ordem_id,
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
                {"detail": "Ordem encerrada não aceita novas evidências."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        arquivos = (
            request.FILES.getlist("anexos")
            or request.FILES.getlist("arquivos")
            or request.FILES.getlist("midia")
        )
        if not arquivos:
            return Response(
                {"detail": "Envie ao menos um arquivo de imagem."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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

        if ordem.status in (
            OrdemServico.Status.PENDENTE,
            OrdemServico.Status.EM_ANDAMENTO,
        ):
            ordem.status = OrdemServico.Status.AGUARDANDO_FORMALIZACAO

        ordem.save(update_fields=["status", "atualizado_em"])

        ordem = (
            OrdemServico.objects.select_related(
                "protocolo",
                "protocolo__servico",
                "protocolo__usuario",
                "unidade",
                "formalizado_por",
            )
            .prefetch_related(Prefetch("anexos", queryset=AnexoOrdemServico.objects.order_by("criado_em")))
            .get(pk=ordem.pk)
        )

        return Response(
            {
                "sucesso": True,
                "anexos_recebidos": criados,
                "ordem_servico": SetorialOrdemServicoSerializer(
                    ordem, context={"request": request}
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )


class FormalizarOrdemServicoView(APIView):
    permission_classes = [IsAuthenticated, IsSetorialStaff]

    @transaction.atomic
    def post(self, request, ordem_id):
        ordem = get_object_or_404(
            OrdemServico.objects.select_for_update().select_related(
                "unidade", "protocolo"
            ),
            pk=ordem_id,
        )
        if not usuario_pode_gerir_ordem(request.user, ordem):
            return Response(
                {"detail": "Ordem não pertence à sua unidade administrativa."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = FormalizarOrdemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if not request.user.check_password(data["senha_assinatura"]):
            return Response(
                {"detail": "Senha de assinatura inválida."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if ordem.status == OrdemServico.Status.CONCLUIDA:
            return Response(
                {"detail": "Ordem de serviço já formalizada."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if ordem.status == OrdemServico.Status.CANCELADA:
            return Response(
                {"detail": "Ordem cancelada não pode ser formalizada."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if ordem.status == OrdemServico.Status.AGUARDANDO_ASSINATURA:
            return Response(
                {
                    "detail": (
                        "Ordem aguardando assinatura hierárquica. "
                        "O assinante designado deve concluir o fluxo em "
                        "/backoffice/assinaturas/<id>/assinar."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        assinatura, momento_assinatura = registrar_assinatura_hash(
            ordem, request.user, data["despacho_tecnico"]
        )
        concluir_os(
            ordem,
            despacho_tecnico=data["despacho_tecnico"],
            observacoes_extras=data.get("observacoes_extras") or "",
            formalizado_por=request.user,
            assinatura_hash=assinatura,
            data_formalizacao=momento_assinatura,
        )

        protocolo = Protocolo.objects.select_for_update().get(pk=ordem.protocolo_id)
        try:
            garantir_protocolo_tramitavel(protocolo)
        except ProtocoloEncerradoError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        equipe = getattr(request.user, "nome", "") or ordem.nome_equipe
        unidade_nome = ordem.unidade.sigla or ordem.unidade.nome if ordem.unidade else ""
        ProtocoloHistorico.objects.create(
            protocolo=protocolo,
            status=protocolo.status,
            descricao=(
                f"Ordem formalizada — {unidade_nome}. "
                "Despacho técnico registrado com assinatura digital."
            ),
            equipe_nome=equipe,
        )
        protocolo_atualizado = concluir_atendimento_setor(
            protocolo,
            ordem,
            despacho_tecnico=data["despacho_tecnico"],
            equipe_nome=equipe,
            unidade_nome=unidade_nome,
        )
        notificar_os_formalizada_ouvidor(ordem, request=request)
        protocolo.refresh_from_db()
        ordem.refresh_from_db()

        ordem = (
            OrdemServico.objects.select_related(
                "protocolo",
                "protocolo__servico",
                "protocolo__usuario",
                "formalizado_por",
            )
            .prefetch_related("anexos")
            .get(pk=ordem.pk)
        )

        return Response(
            {
                "sucesso": True,
                "ordem_servico": SetorialOrdemServicoSerializer(
                    ordem, context={"request": request}
                ).data,
                "protocolo_status": protocolo.status,
                "protocolo_em_revisao": protocolo_atualizado,
                "assinatura_digital_hash": assinatura,
            },
            status=status.HTTP_200_OK,
        )
