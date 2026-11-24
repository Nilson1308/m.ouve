"""API de protocolos, assistente e geocodificação."""

import re

from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.geocoding import reverse_geocode, search_address
from atendimentos.models import AnexoProtocolo, Protocolo, ProtocoloComentario
from atendimentos.sla_cobranca_views import ProtocoloCobrarMixin
from atendimentos.serializers import (
    AnexoSerializer,
    ComentarioSerializer,
    ProtocoloCreateSerializer,
    ProtocoloDetailSerializer,
    ProtocoloListSerializer,
)


def _filtrar_por_categoria_legada(qs, valor: str):
    """Filtro legado `tipo` → categoria do catálogo (slug, nome ou ouvidoria/zeladoria)."""
    from django.db.models import Q

    if not valor:
        return qs
    legado = valor.strip().lower()
    if legado in ("ouvidoria", "zeladoria"):
        return qs.filter(servico__categoria__tipo_legado=legado)
    slug = legado.replace(" ", "_")
    return qs.filter(
        Q(servico__categoria__slug__iexact=slug)
        | Q(servico__categoria__nome__iexact=valor.strip())
    )


class ProtocoloViewSet(ProtocoloCobrarMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    lookup_value_regex = r"[^/]+"
    http_method_names = ["get", "post", "head", "options"]

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)
        if lookup and str(lookup).upper().startswith("PROT-"):
            return get_object_or_404(queryset, codigo=lookup)
        return get_object_or_404(queryset, pk=lookup)

    def get_queryset(self):
        qs = Protocolo.objects.filter(usuario=self.request.user).prefetch_related(
            "anexos",
            "historico",
            "ordens_servico",
            "ordens_servico__unidade",
        )
        status_param = self.request.query_params.get("status")
        categoria_servico = self.request.query_params.get("categoria_servico")
        tipo_param = self.request.query_params.get("tipo")
        if status_param:
            qs = qs.filter(status=status_param)
        if categoria_servico:
            qs = _filtrar_por_categoria_legada(qs, categoria_servico)
        elif tipo_param:
            qs = _filtrar_por_categoria_legada(qs, tipo_param)
        qs = qs.select_related("servico", "servico__categoria")
        if self.action == "retrieve":
            qs = qs.select_related("avaliacao")
        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProtocoloDetailSerializer
        if self.action == "create":
            return ProtocoloCreateSerializer
        return ProtocoloListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = ProtocoloListSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = ProtocoloCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        protocolo = serializer.save()
        self._processar_anexos(request, protocolo)
        out = ProtocoloDetailSerializer(protocolo, context={"request": request}).data
        return Response(out, status=status.HTTP_201_CREATED)

    def _processar_anexos(self, request, protocolo):
        fotos = request.FILES.getlist("fotos[]") or request.FILES.getlist("fotos")
        for foto in fotos:
            AnexoProtocolo.objects.create(
                protocolo=protocolo,
                arquivo=foto,
                tipo_mime=foto.content_type or "image/jpeg",
            )
        audio = request.FILES.get("audio")
        if audio:
            AnexoProtocolo.objects.create(
                protocolo=protocolo,
                arquivo=audio,
                tipo_mime=audio.content_type or "audio/mpeg",
            )

    @action(detail=True, methods=["post"], url_path="cobrar")
    def cobrar(self, request, pk=None):
        return self.cobrar_protocolo(request, self.get_object())

    @action(detail=True, methods=["post"], url_path="responder-diligencia")
    def responder_diligencia(self, request, pk=None):
        from atendimentos.diligencia_views import ProtocoloResponderDiligenciaMixin

        mixin = ProtocoloResponderDiligenciaMixin()
        return mixin.responder_diligencia_protocolo(request, self.get_object())

    @action(detail=True, methods=["post"], url_path="anexos")
    def anexos(self, request, pk=None):
        """Anexa fotos ao protocolo do cidadão (v4.14 — complementação / diligência)."""
        protocolo = self.get_object()
        fotos = request.FILES.getlist("fotos[]") or request.FILES.getlist("fotos")
        if not fotos:
            return Response(
                {"detail": "Envie ao menos um arquivo em fotos[] ou fotos."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        criados = []
        for foto in fotos:
            criados.append(
                AnexoProtocolo.objects.create(
                    protocolo=protocolo,
                    arquivo=foto,
                    tipo_mime=foto.content_type or "image/jpeg",
                )
            )
        serializer = AnexoSerializer(criados, many=True, context={"request": request})
        return Response({"anexos": serializer.data}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="comentarios")
    def comentarios(self, request, codigo=None):
        protocolo = self.get_object()
        texto = request.data.get("texto")
        if not texto:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "Texto obrigatório"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        comentario = ProtocoloComentario.objects.create(
            protocolo=protocolo, autor=request.user, texto=texto
        )
        return Response(
            ComentarioSerializer(comentario).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["get"], url_path="similares")
    def similares(self, request, codigo=None):
        protocolo = self.get_object()
        vizinhos = (
            Protocolo.objects.filter(servico=protocolo.servico)
            .exclude(pk=protocolo.pk)
            .order_by("-data_criacao")[:5]
        )
        itens = []
        for p in vizinhos:
            dados = p.dados_dinamicos or {}
            cat = dados.get("categoria_problema") or dados.get("tema") or p.servico.nome
            item = {
                "id": p.codigo,
                "categoria": cat,
                "descricao": p.descricao[:120],
                "similaridade": 0.75,
            }
            if protocolo.localizacao and p.localizacao:
                from django.contrib.gis.db.models.functions import Distance

                dist = (
                    Protocolo.objects.filter(pk=p.pk)
                    .annotate(dist=Distance("localizacao", protocolo.localizacao))
                    .values_list("dist", flat=True)
                    .first()
                )
                if dist:
                    item["distancia_metros"] = int(dist.m)
            itens.append(item)
        return Response({"similares": itens})


class AdminEstatisticasView(APIView):
    def get(self, request):
        qs = Protocolo.objects.all()
        data_inicio = request.query_params.get("data_inicio")
        data_fim = request.query_params.get("data_fim")
        categoria_servico = request.query_params.get("categoria_servico")
        tipo = request.query_params.get("tipo")
        if data_inicio:
            qs = qs.filter(data_criacao__date__gte=data_inicio)
        if data_fim:
            qs = qs.filter(data_criacao__date__lte=data_fim)
        if categoria_servico:
            qs = _filtrar_por_categoria_legada(qs, categoria_servico)
        elif tipo:
            qs = _filtrar_por_categoria_legada(qs, tipo)

        por_status = {
            row["status"]: row["total"]
            for row in qs.values("status").annotate(total=Count("id"))
        }
        por_servico = {
            row["servico__nome"]: row["total"]
            for row in qs.values("servico__nome").annotate(total=Count("id"))
        }
        resolvidos = qs.filter(status=Protocolo.Status.RESOLVIDO)
        duracao_media = resolvidos.annotate(
            duracao=ExpressionWrapper(
                F("data_atualizacao") - F("data_criacao"),
                output_field=DurationField(),
            )
        ).aggregate(media=Avg("duracao"))
        media_dias = 0.0
        if duracao_media["media"]:
            media_dias = duracao_media["media"].total_seconds() / 86400

        total = qs.count()
        taxa = (por_status.get("resolvido", 0) / total) if total else 0.0

        return Response(
            {
                "total_protocolos": total,
                "por_status": por_status,
                "por_categoria": por_servico,
                "tempo_medio_resolucao_dias": round(media_dias, 1),
                "taxa_resolucao": round(taxa, 2),
            }
        )


class AssistenteAnalisarView(APIView):
    """NLP stub para classificação de relatos."""

    def post(self, request):
        texto = (request.data.get("texto") or "").lower()
        categoria = "Via Pública"
        sub = "Buraco/Pavimentação"
        urgencia = "media"
        keywords = []
        if "luz" in texto or "poste" in texto or "iluminação" in texto:
            categoria = "Iluminação Pública"
            sub = "Lâmpada/Poste"
            keywords = ["iluminação", "poste"]
        elif "buraco" in texto or "via" in texto:
            keywords = ["buraco", "via pública", "pavimentação"]
        endereco = None
        match = re.search(r"rua\s+[^,]+", request.data.get("texto", ""), re.I)
        if match:
            endereco = match.group(0).title()
        return Response(
            {
                "categoria_sugerida": categoria,
                "subcategoria": sub,
                "endereco_detectado": endereco,
                "confianca": 0.92,
                "keywords": keywords or ["espaco_publico"],
                "urgencia_estimada": urgencia,
            }
        )


class AssistenteTranscreverView(APIView):
    def post(self, request):
        audio = request.FILES.get("audio")
        if not audio:
            return Response(
                {
                    "error": {
                        "code": "AUDIO_REQUIRED",
                        "message": "Envie um arquivo de áudio no campo 'audio'.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if audio.size > 25 * 1024 * 1024:
            return Response(
                {
                    "error": {
                        "code": "AUDIO_TOO_LARGE",
                        "message": "Áudio muito grande (máx. 25 MB).",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        from atendimentos.speech_transcription import transcrever_upload_audio

        try:
            texto, confianca = transcrever_upload_audio(audio)
        except ValueError as exc:
            return Response(
                {"error": {"code": "TRANSCRIPTION_EMPTY", "message": str(exc)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            import logging

            logging.getLogger(__name__).exception(
                "Falha na transcrição de áudio: %s", exc
            )
            return Response(
                {
                    "error": {
                        "code": "TRANSCRIPTION_FAILED",
                        "message": "Não foi possível transcrever o áudio. Tente novamente.",
                    }
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "texto": texto,
                "confianca": confianca,
                "idioma": "pt-BR",
            }
        )


class GeocodeReverseView(APIView):
    def get(self, request):
        try:
            lat = float(request.query_params.get("latitude"))
            lng = float(request.query_params.get("longitude"))
        except (TypeError, ValueError):
            return Response(
                {"error": {"code": "INVALID_COORDS", "message": "Latitude e longitude inválidas."}},
                status=400,
            )

        resultado = reverse_geocode(lat, lng)
        if not resultado:
            return Response(
                {
                    "sucesso": False,
                    "endereco_completo": f"Ponto ({lat:.6f}, {lng:.6f})",
                    "mensagem": (
                        "Não foi possível obter o endereço automaticamente. "
                        "As coordenadas foram registradas para validação pela equipe."
                    ),
                }
            )
        return Response({"sucesso": True, **resultado})


class GeocodeSearchView(APIView):
    def get(self, request):
        query = request.query_params.get("query", "")
        resultados = search_address(query)
        if not resultados:
            return Response(
                {
                    "sucesso": False,
                    "resultados": [],
                    "mensagem": "Nenhum endereço encontrado. Tente outro termo ou marque no mapa.",
                }
            )
        return Response({"sucesso": True, "resultados": resultados})
