"""Serializers de protocolos e ordens de serviço."""

import json

from django.contrib.gis.geos import Point
from rest_framework import serializers

from atendimentos.models import (
    AnexoProtocolo,
    AvaliacaoProtocolo,
    OrdemServico,
    Protocolo,
    ProtocoloComentario,
    ProtocoloHistorico,
)
from catalogo.models import ServicoCatalogo
from catalogo.serializers import ServicoCatalogoResumoSerializer
from catalogo.validators import validar_dados_dinamicos


class AnexoSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    tipo = serializers.SerializerMethodField()
    mime_type = serializers.CharField(source="tipo_mime", read_only=True)
    nome_arquivo = serializers.SerializerMethodField()
    nome = serializers.SerializerMethodField()
    criado_em = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)

    class Meta:
        model = AnexoProtocolo
        fields = (
            "id",
            "url",
            "tipo",
            "mime_type",
            "nome_arquivo",
            "nome",
            "criado_em",
        )

    def get_url(self, obj):
        from ouvia_core.url_utils import public_absolute_uri

        request = self.context.get("request")
        return public_absolute_uri(request, obj.arquivo.url if obj.arquivo else None)

    def get_tipo(self, obj):
        return obj.tipo_mime or "application/octet-stream"

    def get_nome_arquivo(self, obj):
        if obj.arquivo and obj.arquivo.name:
            return obj.arquivo.name.rsplit("/", 1)[-1]
        return ""

    def get_nome(self, obj):
        return self.get_nome_arquivo(obj)


class OrdemServicoSerializer(serializers.ModelSerializer):
    secretaria = serializers.SerializerMethodField()

    class Meta:
        model = OrdemServico
        fields = (
            "id",
            "secretaria",
            "nome_equipe",
            "descricao",
            "prazo_horas",
            "status",
            "criado_em",
            "atualizado_em",
        )
        read_only_fields = fields

    def get_secretaria(self, obj):
        if obj.unidade_id:
            return obj.unidade.nome
        return ""


class ProtocoloServicoMixin(serializers.Serializer):
    """Campos derivados do catálogo (compatibilidade de leitura da API)."""

    servico = ServicoCatalogoResumoSerializer(read_only=True)
    servico_id = serializers.UUIDField(source="servico.id", read_only=True)
    dados_dinamicos = serializers.JSONField(read_only=True)
    tipo = serializers.SerializerMethodField()
    categoria = serializers.SerializerMethodField()
    tipo_manifestacao = serializers.SerializerMethodField()

    def get_tipo(self, obj):
        cat = obj.servico.categoria
        if cat and cat.tipo_legado:
            return cat.tipo_legado
        if cat:
            return cat.slug.replace("_", " ")
        return ""

    def get_categoria(self, obj):
        dados = obj.dados_dinamicos or {}
        if dados.get("categoria_problema"):
            return dados["categoria_problema"]
        if dados.get("tema"):
            return dados["tema"]
        return obj.servico.nome

    def get_tipo_manifestacao(self, obj):
        return (obj.dados_dinamicos or {}).get("tipo_manifestacao", "")


class ProtocoloListSerializer(ProtocoloServicoMixin, serializers.ModelSerializer):
    id = serializers.CharField(source="codigo")
    data_criacao = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    data_atualizacao = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    localizacao = serializers.SerializerMethodField()
    anexos = AnexoSerializer(many=True, read_only=True)

    class Meta:
        model = Protocolo
        fields = (
            "id",
            "servico",
            "servico_id",
            "dados_dinamicos",
            "tipo",
            "categoria",
            "tipo_manifestacao",
            "descricao",
            "status",
            "data_criacao",
            "data_atualizacao",
            "localizacao",
            "anexos",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and getattr(request, "user", None) and request.user.is_authenticated:
            from atendimentos.sla_cobranca_views import campos_cobranca_protocolo_pwa
            from atendimentos.services.diligencia_service import campos_diligencia_pwa

            data.update(campos_cobranca_protocolo_pwa(instance, request.user))
            data.update(campos_diligencia_pwa(instance, request=request))
        return data

    def get_localizacao(self, obj):
        if not obj.localizacao and not obj.endereco_texto:
            return None
        if obj.localizacao:
            return {
                "endereco": obj.endereco_texto,
                "latitude": obj.localizacao.y,
                "longitude": obj.localizacao.x,
            }
        return {"endereco": obj.endereco_texto, "latitude": None, "longitude": None}


class HistoricoSerializer(serializers.ModelSerializer):
    data = serializers.DateTimeField(source="registrado_em", format="%Y-%m-%dT%H:%M:%SZ")
    equipe = serializers.CharField(source="equipe_nome", allow_blank=True)

    class Meta:
        model = ProtocoloHistorico
        fields = ("data", "status", "descricao", "equipe")


class ProtocoloDetailSerializer(ProtocoloListSerializer):
    descricao = serializers.SerializerMethodField()
    campos_solicitacao = serializers.SerializerMethodField()
    historico = HistoricoSerializer(many=True, read_only=True)
    equipe = serializers.SerializerMethodField()
    ordens_servico = OrdemServicoSerializer(many=True, read_only=True)
    pode_avaliar = serializers.SerializerMethodField()
    avaliacao = serializers.SerializerMethodField()

    class Meta(ProtocoloListSerializer.Meta):
        fields = ProtocoloListSerializer.Meta.fields + (
            "campos_solicitacao",
            "historico",
            "equipe",
            "ordens_servico",
            "pode_avaliar",
            "avaliacao",
        )

    def get_descricao(self, obj):
        from atendimentos.chat_resumo import descricao_exibicao_cidadao

        return descricao_exibicao_cidadao(obj)

    def get_campos_solicitacao(self, obj):
        from atendimentos.chat_resumo import montar_campos_protocolo_publico

        return montar_campos_protocolo_publico(obj.servico, obj.dados_dinamicos)

    def get_equipe(self, obj):
        ordem = obj.ordens_servico.filter(nome_equipe__gt="").first()
        if not ordem:
            return None
        return {"id": str(ordem.id), "nome": ordem.nome_equipe}

    def _avaliacao_objeto(self, obj):
        try:
            return obj.avaliacao
        except AvaliacaoProtocolo.DoesNotExist:
            return None

    def get_pode_avaliar(self, obj):
        if obj.status != Protocolo.Status.RESOLVIDO:
            return False
        return self._avaliacao_objeto(obj) is None

    def get_avaliacao(self, obj):
        av = self._avaliacao_objeto(obj)
        if not av:
            return None
        return {
            "nota": av.nota,
            "comentario": av.comentario or "",
            "criada_em": av.criada_em.strftime("%Y-%m-%dT%H:%M:%SZ")
            if av.criada_em
            else None,
        }


class ProtocoloCreateSerializer(serializers.Serializer):
    servico_id = serializers.UUIDField()
    dados_dinamicos = serializers.JSONField(required=False, default=dict)
    descricao = serializers.CharField()
    endereco = serializers.CharField(required=False, allow_blank=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)

    def validate_dados_dinamicos(self, value):
        if isinstance(value, str):
            try:
                return json.loads(value) if value.strip() else {}
            except json.JSONDecodeError as exc:
                raise serializers.ValidationError(
                    "dados_dinamicos deve ser um objeto JSON válido."
                ) from exc
        return value if value is not None else {}

    def validate_servico_id(self, value):
        try:
            servico = ServicoCatalogo.objects.get(pk=value, ativo=True, is_template=False)
        except ServicoCatalogo.DoesNotExist as exc:
            raise serializers.ValidationError("Serviço não encontrado ou inativo.") from exc
        self.context["servico"] = servico
        return value

    def validate(self, attrs):
        servico = self.context.get("servico")
        if not servico:
            raise serializers.ValidationError({"servico_id": "Serviço inválido."})

        dados = attrs.get("dados_dinamicos") or {}
        attrs["dados_dinamicos"] = validar_dados_dinamicos(servico.schema_formulario, dados)

        for key in ("latitude", "longitude"):
            val = attrs.get(key)
            if val is not None and isinstance(val, str):
                try:
                    attrs[key] = float(val)
                except ValueError as exc:
                    raise serializers.ValidationError({key: "Valor numérico inválido"}) from exc

        if servico.exige_localizacao:
            if attrs.get("latitude") is None or attrs.get("longitude") is None:
                raise serializers.ValidationError(
                    {
                        "latitude": (
                            "Latitude e longitude são obrigatórias para este serviço."
                        )
                    }
                )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        servico = self.context["servico"]
        protocolo = Protocolo(
            codigo=Protocolo.gerar_codigo(),
            usuario=user,
            servico=servico,
            dados_dinamicos=validated_data.get("dados_dinamicos") or {},
            descricao=validated_data["descricao"],
            endereco_texto=validated_data.get("endereco", ""),
            resposta_cidadao="",
            observacoes_internas="",
        )
        lat = validated_data.get("latitude")
        lng = validated_data.get("longitude")
        if lat is not None and lng is not None:
            protocolo.localizacao = Point(lng, lat, srid=4326)
        from atendimentos.services.protocolo_localidade import sincronizar_localidade_protocolo

        sincronizar_localidade_protocolo(protocolo, persistir=False)
        protocolo.save()
        from atendimentos.services.equipamento_protocolo import sincronizar_equipamento_no_protocolo

        sincronizar_equipamento_no_protocolo(protocolo)
        from atendimentos.services.triagem_service import executar_triagem_protocolo

        executar_triagem_protocolo(protocolo)
        from atendimentos.services.fluxo_governanca_service import (
            processar_governanca_entrada_protocolo,
        )

        processar_governanca_entrada_protocolo(protocolo)
        return protocolo


class ComentarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProtocoloComentario
        fields = ("id", "texto", "criado_em")
