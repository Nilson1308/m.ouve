"""Serializers da Super OS (incidente mestre)."""

from rest_framework import serializers

from atendimentos.backoffice_serializers import (
    BackofficeOrdemServicoDetalheSerializer,
    BackofficeProtocoloHistoricoSerializer,
    BackofficeServicoResumoSerializer,
    calcular_sla,
    extrair_urgencia,
    formatar_historico_chat,
    mesclar_dados_coletados,
)
from atendimentos.models import Protocolo, SuperOS


class SuperOSSerializer(serializers.ModelSerializer):
    protocolos_filhos_ids = serializers.SerializerMethodField()
    quantidade_protocolos = serializers.SerializerMethodField()

    class Meta:
        model = SuperOS
        fields = (
            "id",
            "codigo",
            "titulo_resumo",
            "descricao_geral",
            "status",
            "latitude_centro",
            "longitude_centro",
            "criado_em",
            "atualizado_em",
            "protocolos_filhos_ids",
            "quantidade_protocolos",
        )
        read_only_fields = fields

    def get_protocolos_filhos_ids(self, obj):
        if hasattr(obj, "_prefetched_filhos_ids"):
            return obj._prefetched_filhos_ids
        return [str(pk) for pk in obj.protocolos_filhos.values_list("pk", flat=True)]

    def get_quantidade_protocolos(self, obj):
        if hasattr(obj, "_quantidade_filhos"):
            return obj._quantidade_filhos
        return obj.protocolos_filhos.count()


class SuperOSProtocoloFilhoDossieSerializer(serializers.ModelSerializer):
    cidadao = serializers.SerializerMethodField()
    dados_coletados = serializers.SerializerMethodField()
    historico_chat = serializers.SerializerMethodField()
    historico_protocolo = BackofficeProtocoloHistoricoSerializer(
        source="historico", many=True, read_only=True
    )
    servico = BackofficeServicoResumoSerializer(read_only=True)
    sla = serializers.SerializerMethodField()
    urgencia = serializers.SerializerMethodField()
    localizacao = serializers.SerializerMethodField()

    class Meta:
        model = Protocolo
        fields = (
            "id",
            "codigo",
            "status",
            "descricao",
            "endereco_texto",
            "data_criacao",
            "data_atualizacao",
            "cidadao",
            "servico",
            "dados_coletados",
            "historico_chat",
            "historico_protocolo",
            "sla",
            "urgencia",
            "localizacao",
        )
        read_only_fields = fields

    def get_cidadao(self, obj):
        u = obj.usuario
        return {
            "id": str(u.id),
            "nome": u.nome,
            "telefone": u.telefone or "",
            "email": u.email or "",
        }

    def get_dados_coletados(self, obj):
        return mesclar_dados_coletados(obj)

    def get_historico_chat(self, obj):
        request = self.context.get("request")
        sessao = getattr(obj, "sessao_chat", None)
        return formatar_historico_chat(sessao, request)

    def get_sla(self, obj):
        return calcular_sla(obj)

    def get_urgencia(self, obj):
        return extrair_urgencia(obj.dados_dinamicos)

    def get_localizacao(self, obj):
        payload = {"endereco": obj.endereco_texto or ""}
        if obj.localizacao:
            payload["latitude"] = obj.localizacao.y
            payload["longitude"] = obj.localizacao.x
        else:
            payload["latitude"] = None
            payload["longitude"] = None
        return payload


class SuperOSDetalheSerializer(SuperOSSerializer):
    protocolos_filhos = SuperOSProtocoloFilhoDossieSerializer(many=True, read_only=True)
    centroide = serializers.SerializerMethodField()
    ordens_servico_ids = serializers.SerializerMethodField()
    ordens_servico = BackofficeOrdemServicoDetalheSerializer(many=True, read_only=True)
    sla = serializers.SerializerMethodField()
    urgencia = serializers.SerializerMethodField()

    class Meta(SuperOSSerializer.Meta):
        fields = SuperOSSerializer.Meta.fields + (
            "protocolos_filhos",
            "centroide",
            "ordens_servico_ids",
            "ordens_servico",
            "sla",
            "urgencia",
        )

    def get_centroide(self, obj):
        if obj.latitude_centro is not None and obj.longitude_centro is not None:
            return {"latitude": obj.latitude_centro, "longitude": obj.longitude_centro}
        filhos = list(obj.protocolos_filhos.all())
        lats, lons = [], []
        for p in filhos:
            if p.localizacao:
                lats.append(p.localizacao.y)
                lons.append(p.localizacao.x)
        if not lats:
            return None
        return {
            "latitude": sum(lats) / len(lats),
            "longitude": sum(lons) / len(lons),
        }

    def get_ordens_servico_ids(self, obj):
        return [str(pk) for pk in obj.ordens_servico.values_list("pk", flat=True)]

    def get_sla(self, obj):
        filhos = list(obj.protocolos_filhos.all())
        if not filhos:
            return None
        from atendimentos.kanban_services import _agregar_sla_filhos

        return _agregar_sla_filhos(filhos)

    def get_urgencia(self, obj):
        from atendimentos.kanban_services import _agregar_urgencia_filhos

        return _agregar_urgencia_filhos(list(obj.protocolos_filhos.all()))


class CriarRetroativaSuperOSSerializer(serializers.Serializer):
    protocolo_ancora_id = serializers.UUIDField()
    protocolos_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
        min_length=1,
    )
    titulo_resumo = serializers.CharField(max_length=255)
    descricao_geral = serializers.CharField(required=False, allow_blank=True, default="")


class AnexarProtocoloSuperOSSerializer(serializers.Serializer):
    protocolo_id = serializers.UUIDField()


class AgruparMapaSuperOSSerializer(serializers.Serializer):
    protocolos_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
        min_length=1,
    )
    titulo_resumo = serializers.CharField(max_length=255)
    descricao_geral = serializers.CharField(required=False, allow_blank=True, default="")