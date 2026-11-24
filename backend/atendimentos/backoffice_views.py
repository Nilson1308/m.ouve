"""Views da API de backoffice — mesa de trabalho e scatter-gather."""

from datetime import timedelta

from django.db import transaction
from django.db.models import Count, DateTimeField, F, Prefetch, Q
from django.db.models.expressions import ExpressionWrapper
from django.db.models.functions import Now
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters import rest_framework as filters
import mimetypes

from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.backoffice_serializers import (
    BackofficeOrdemServicoDetalheSerializer,
    BackofficeOrdemServicoSerializer,
    BackofficeProtocoloDetalheSerializer,
    BackofficeProtocoloKanbanSerializer,
    ConcluirOrdemServicoSerializer,
    DespacharProtocoloSerializer,
    DevolverOrdemServicoSerializer,
    UnidadeAdministrativaSerializer,
    ValidarProtocoloSerializer,
    calcular_sla,
    extrair_urgencia,
)
from atendimentos.notificacoes_internas import notificar_despacho_scatter
from atendimentos.services.escopo_dados import queryset_protocolos_escopo
from atendimentos.backoffice_services import (
    ProtocoloEncerradoError,
    concluir_atendimento_setor,
    garantir_protocolo_tramitavel,
    get_ordem_servico_backoffice,
    get_protocolo_backoffice,
    marcar_ordem_concluida,
    protocolo_esta_encerrado,
)
from atendimentos.models import (
    AnexoOrdemServico,
    OrdemServico,
    Protocolo,
    ProtocoloHistorico,
)
from catalogo.models import UnidadeAdministrativa
from core_auth.permissions import IsBackofficeStaff
from ouvia_core.pagination import ContractPagination


class BackofficeProtocoloFilterSet(filters.FilterSet):
    status = filters.BaseInFilter(field_name="status")
    busca = filters.CharFilter(method="filter_busca")
    urgencia = filters.BaseInFilter(method="filter_urgencia")
    sla_vencido = filters.BooleanFilter(method="filter_sla_vencido")
    unidade_id = filters.BaseInFilter(
        field_name="ordens_servico__unidade_id",
        distinct=True,
    )
    servico_id = filters.BaseInFilter(field_name="servico_id")
    bairro = filters.BaseInFilter(method="filter_bairro")
    equipamento_id = filters.UUIDFilter(field_name="equipamento_id")
    apenas_cobrados = filters.BooleanFilter(method="filter_apenas_cobrados")

    class Meta:
        model = Protocolo
        fields = ("status",)

    def filter_busca(self, queryset, name, value):
        if not value:
            return queryset
        termo = value.strip()
        return queryset.filter(
            Q(codigo__icontains=termo) | Q(descricao__icontains=termo)
        )

    def filter_urgencia(self, queryset, name, value):
        valores = value if isinstance(value, (list, tuple)) else [value]
        valores = [str(v).strip().lower() for v in valores if str(v).strip()]
        if not valores:
            return queryset
        q = Q()
        for val in valores:
            q |= (
                Q(dados_dinamicos__urgencia__iexact=val)
                | Q(dados_dinamicos__prioridade__iexact=val)
                | Q(dados_dinamicos__urgencia_estimada__iexact=val)
            )
        return queryset.filter(q).distinct()

    def filter_bairro(self, queryset, name, value):
        valores = value if isinstance(value, (list, tuple)) else [value]
        valores = [str(v).strip() for v in valores if str(v).strip()]
        if not valores:
            return queryset
        q = Q()
        for bairro in valores:
            q |= (
                Q(dados_dinamicos__bairro__iexact=bairro)
                | Q(dados_dinamicos__bairro__icontains=bairro)
                | Q(endereco_texto__icontains=bairro)
                | Q(usuario__endereco__bairro__iexact=bairro)
            )
        return queryset.filter(q).distinct()

    def filter_sla_vencido(self, queryset, name, value):
        if value is None:
            return queryset
        qs = queryset.annotate(
            _prazo_sla=ExpressionWrapper(
                F("data_criacao") + timedelta(hours=1) * F("servico__sla_horas"),
                output_field=DateTimeField(),
            )
        )
        if value:
            return qs.filter(_prazo_sla__lt=Now())
        return qs.filter(_prazo_sla__gte=Now())

    def filter_apenas_cobrados(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(qtd_cobrancas_cidadao__gte=1)


class BackofficeFiltrosMesaView(APIView):
    """Opções para filtros avançados da Mesa de Trabalho."""

    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request):
        from catalogo.models import ServicoCatalogo

        from atendimentos.services.dashboard_filters import listar_bairros_protocolos

        bairros_set = listar_bairros_protocolos(request.user, apenas_com_geo=False)

        servicos = [
            {"id": str(s.id), "nome": s.nome}
            for s in ServicoCatalogo.objects.filter(ativo=True)
            .select_related("categoria")
            .order_by("nome")[:500]
        ]

        return Response(
            {
                "bairros": bairros_set,
                "servicos": servicos,
                "status": [
                    {"value": key, "label": label}
                    for key, label in Protocolo.Status.choices
                ],
                "urgencias": [
                    {"value": "baixa", "label": "Baixa"},
                    {"value": "media", "label": "Média"},
                    {"value": "alta", "label": "Alta"},
                    {"value": "critica", "label": "Crítica"},
                ],
            }
        )


class BackofficeUnidadesListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsBackofficeStaff]
    serializer_class = UnidadeAdministrativaSerializer
    queryset = UnidadeAdministrativa.objects.filter(ativo=True).order_by("nome")
    pagination_class = None


class BackofficeProtocoloListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsBackofficeStaff]
    serializer_class = BackofficeProtocoloKanbanSerializer
    pagination_class = ContractPagination
    filterset_class = BackofficeProtocoloFilterSet
    ordering_fields = ("data_criacao", "status", "codigo")
    ordering = ("-data_criacao",)

    def get_queryset(self):
        ordens_qs = OrdemServico.objects.select_related("unidade").order_by("criado_em")
        base = (
            Protocolo.objects.select_related(
                "servico",
                "servico__categoria",
                "usuario",
                "equipamento",
            )
            .prefetch_related(Prefetch("ordens_servico", queryset=ordens_qs))
            .annotate(_tem_anexos=Count("anexos", distinct=True))
        )
        return queryset_protocolos_escopo(self.request.user, base_qs=base)


class BackofficeDespacharProtocoloView(APIView):
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    @transaction.atomic
    def post(self, request, protocolo_id):
        protocolo = get_protocolo_backoffice(
            protocolo_id,
            Protocolo.objects.select_for_update().select_related("servico"),
            user=request.user,
        )
        try:
            garantir_protocolo_tramitavel(protocolo)
        except ProtocoloEncerradoError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DespacharProtocoloSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        unidade_ids = [item["unidade_id"] for item in data["ordens"]]
        if len(unidade_ids) != len(set(unidade_ids)):
            return Response(
                {"detail": "Cada unidade só pode receber uma ordem por despacho."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        unidades = {
            u.id: u
            for u in UnidadeAdministrativa.objects.filter(
                pk__in=unidade_ids, ativo=True
            )
        }
        faltantes = [str(uid) for uid in unidade_ids if uid not in unidades]
        if faltantes:
            return Response(
                {
                    "detail": "Unidade administrativa inválida ou inativa.",
                    "unidade_ids": faltantes,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        ordens_criadas = []
        for item in data["ordens"]:
            unidade = unidades[item["unidade_id"]]
            ordem = OrdemServico.objects.create(
                protocolo=protocolo,
                unidade=unidade,
                descricao=item["instrucao"],
                prazo_horas=item["prazo_horas"],
                nome_equipe=unidade.sigla or unidade.nome,
                status=OrdemServico.Status.PENDENTE,
                despachado_por=request.user,
            )
            ordens_criadas.append(ordem)

        protocolo.status = Protocolo.Status.EM_ANDAMENTO
        protocolo.save(update_fields=["status", "data_atualizacao"])

        obs = (data.get("observacao_geral") or "").strip()
        partes = [
            f"Despacho scatter-gather com {len(ordens_criadas)} ordem(ns) de serviço.",
        ]
        if obs:
            partes.append(f"Observação geral: {obs}")
        from atendimentos.services.triagem_service import texto_auditoria_despacho_triagem

        auditoria = texto_auditoria_despacho_triagem(protocolo, unidade_ids)
        if auditoria:
            partes.append(auditoria)
        descricao_hist = " ".join(partes)

        ProtocoloHistorico.objects.create(
            protocolo=protocolo,
            status=Protocolo.Status.EM_ANDAMENTO,
            descricao=descricao_hist,
            equipe_nome=getattr(request.user, "nome", "") or "",
        )

        notificar_despacho_scatter(protocolo, ordens_criadas, request=request)

        from atendimentos.notificacoes_cidadao import notificar_status_protocolo

        notificar_status_protocolo(protocolo, Protocolo.Status.EM_ANDAMENTO)

        protocolo.refresh_from_db()
        ordens_qs = protocolo.ordens_servico.select_related("unidade").order_by(
            "criado_em"
        )
        protocolo_ser = BackofficeProtocoloKanbanSerializer(protocolo)
        return Response(
            {
                "protocolo": protocolo_ser.data,
                "ordens_servico": BackofficeOrdemServicoSerializer(
                    ordens_qs, many=True
                ).data,
                "despachado_em": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "urgencia": extrair_urgencia(protocolo.dados_dinamicos),
            },
            status=status.HTTP_201_CREATED,
        )


def _protocolo_detalhe_queryset():
    ordens_qs = (
        OrdemServico.objects.select_related("unidade")
        .prefetch_related("anexos")
        .order_by("criado_em")
    )
    historico_qs = ProtocoloHistorico.objects.order_by("registrado_em")
    return (
        Protocolo.objects.select_related(
            "servico",
            "servico__categoria",
            "usuario",
            "sessao_chat",
        )
        .prefetch_related(
            Prefetch("ordens_servico", queryset=ordens_qs),
            Prefetch("historico", queryset=historico_qs),
        )
        .annotate(_tem_anexos=Count("anexos", distinct=True))
    )


class BackofficeProtocoloDetalheView(APIView):
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request, protocolo_id):
        protocolo = get_protocolo_backoffice(
            protocolo_id, _protocolo_detalhe_queryset(), user=request.user
        )
        serializer = BackofficeProtocoloDetalheSerializer(
            protocolo, context={"request": request}
        )
        return Response(serializer.data)


class BackofficeConcluirOrdemServicoView(APIView):
    permission_classes = [IsAuthenticated, IsBackofficeStaff]
    parser_classes = [MultiPartParser, FormParser]

    @transaction.atomic
    def post(self, request, ordem_id):
        ordem = get_ordem_servico_backoffice(ordem_id, user=request.user)
        ordem = OrdemServico.objects.select_for_update().select_related(
            "protocolo", "unidade"
        ).get(pk=ordem.pk)
        if ordem.status == OrdemServico.Status.CANCELADA:
            return Response(
                {"detail": "Ordem de serviço cancelada não pode ser concluída."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if ordem.status == OrdemServico.Status.CONCLUIDA:
            return Response(
                {"detail": "Ordem de serviço já está concluída."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ConcluirOrdemServicoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        observacoes = serializer.validated_data.get("observacoes_execucao") or ""

        arquivos = (
            request.FILES.getlist("anexos")
            or request.FILES.getlist("arquivos")
            or request.FILES.getlist("midia")
        )
        tipos_raw = request.data.getlist("tipo_evidencia")

        marcar_ordem_concluida(ordem, observacoes=observacoes)

        anexos_criados = []
        for idx, arquivo in enumerate(arquivos):
            tipo_ev = (
                tipos_raw[idx].strip()
                if idx < len(tipos_raw) and tipos_raw[idx]
                else AnexoOrdemServico.TipoEvidencia.DEPOIS
            )
            if tipo_ev not in dict(AnexoOrdemServico.TipoEvidencia.choices):
                tipo_ev = AnexoOrdemServico.TipoEvidencia.DEPOIS
            guessed, _ = mimetypes.guess_type(arquivo.name)
            anexo = AnexoOrdemServico.objects.create(
                ordem=ordem,
                arquivo=arquivo,
                nome_original=arquivo.name,
                tipo_mime=guessed or getattr(arquivo, "content_type", "") or "",
                tipo_evidencia=tipo_ev,
            )
            anexos_criados.append(anexo)

        equipe = getattr(request.user, "nome", "") or ordem.nome_equipe
        protocolo = Protocolo.objects.select_for_update().get(pk=ordem.protocolo_id)
        ProtocoloHistorico.objects.create(
            protocolo=protocolo,
            status=protocolo.status,
            descricao=(
                f"Ordem concluída — {ordem.unidade.sigla or ordem.unidade.nome}. "
                f"{len(anexos_criados)} anexo(s) registrado(s)."
            ),
            equipe_nome=equipe,
        )

        unidade_nome = ordem.unidade.sigla or ordem.unidade.nome if ordem.unidade else ""
        protocolo_atualizado = concluir_atendimento_setor(
            protocolo,
            ordem,
            despacho_tecnico=ordem.despacho_tecnico,
            equipe_nome=equipe,
            unidade_nome=unidade_nome,
        )
        protocolo.refresh_from_db()

        ordem.refresh_from_db()
        return Response(
            {
                "ordem_servico": BackofficeOrdemServicoDetalheSerializer(
                    ordem, context={"request": request}
                ).data,
                "protocolo_status": protocolo.status,
                "protocolo_em_revisao": protocolo_atualizado,
                "concluido_em": ordem.concluido_em.strftime("%Y-%m-%dT%H:%M:%SZ")
                if ordem.concluido_em
                else None,
            },
            status=status.HTTP_200_OK,
        )


class BackofficeValidarProtocoloView(APIView):
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    @transaction.atomic
    def post(self, request, protocolo_id):
        protocolo = get_protocolo_backoffice(
            protocolo_id,
            Protocolo.objects.select_for_update().select_related("usuario"),
            user=request.user,
        )
        if protocolo_esta_encerrado(protocolo):
            return Response(
                {
                    "detail": (
                        f"O protocolo {protocolo.codigo} já está encerrado "
                        f"({protocolo.get_status_display()}). "
                        "Não é possível validar novamente."
                    ),
                    "status_atual": protocolo.status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if protocolo.status != Protocolo.Status.AGUARDANDO_REVISAO:
            return Response(
                {
                    "detail": (
                        "O protocolo só pode ser validado quando estiver em "
                        "'aguardando_revisao' (retorno do setor concluído). "
                        "A conclusão definitiva ao cidadão ocorre apenas nesta etapa."
                    ),
                    "status_atual": protocolo.status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ValidarProtocoloSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        protocolo.resposta_cidadao = data["resposta_cidadao"].strip()
        protocolo.observacoes_internas = (data.get("observacoes_internas") or "").strip()
        protocolo.status = Protocolo.Status.RESOLVIDO
        protocolo.save(
            update_fields=[
                "resposta_cidadao",
                "observacoes_internas",
                "status",
                "data_atualizacao",
            ]
        )

        ProtocoloHistorico.objects.create(
            protocolo=protocolo,
            status=Protocolo.Status.RESOLVIDO,
            descricao="Protocolo validado e encerrado pelo gestor da ouvidoria.",
            equipe_nome=getattr(request.user, "nome", "") or "",
        )

        from atendimentos.notificacoes_cidadao import notificar_status_protocolo

        notificar_status_protocolo(protocolo, Protocolo.Status.RESOLVIDO)

        return Response(
            {
                "sucesso": True,
                "protocolo": BackofficeProtocoloDetalheSerializer(
                    get_protocolo_backoffice(
                        protocolo.pk,
                        _protocolo_detalhe_queryset(),
                        user=request.user,
                    ),
                    context={"request": request},
                ).data,
                "mensagem_enviada": True,
            },
            status=status.HTTP_200_OK,
        )


class BackofficeDevolverOrdemServicoView(APIView):
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    @transaction.atomic
    def post(self, request, ordem_id):
        ordem = get_ordem_servico_backoffice(ordem_id, user=request.user)
        ordem = OrdemServico.objects.select_for_update().select_related(
            "protocolo", "unidade"
        ).get(pk=ordem.pk)
        serializer = DevolverOrdemServicoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if ordem.status == OrdemServico.Status.CANCELADA:
            return Response(
                {"detail": "Ordem cancelada não pode ser devolvida."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ordem.status = OrdemServico.Status.EM_ANDAMENTO
        ordem.concluido_em = None
        ordem.save(update_fields=["status", "concluido_em", "atualizado_em"])

        protocolo = Protocolo.objects.select_for_update().get(pk=ordem.protocolo_id)
        if protocolo.status == Protocolo.Status.AGUARDANDO_REVISAO:
            protocolo.status = Protocolo.Status.EM_ANDAMENTO
            protocolo.save(update_fields=["status", "data_atualizacao"])

        descricao = (
            f"Ordem devolvida à {ordem.unidade.sigla or ordem.unidade.nome}. "
            f"Motivo: {data['motivo']}. Justificativa: {data['justificativa']}"
        )
        ProtocoloHistorico.objects.create(
            protocolo=protocolo,
            status=protocolo.status,
            descricao=descricao,
            equipe_nome=getattr(request.user, "nome", "") or "",
        )

        ordem.refresh_from_db()
        protocolo.refresh_from_db()
        return Response(
            {
                "sucesso": True,
                "ordem_servico": BackofficeOrdemServicoDetalheSerializer(
                    ordem, context={"request": request}
                ).data,
                "protocolo_status": protocolo.status,
            },
            status=status.HTTP_200_OK,
        )
