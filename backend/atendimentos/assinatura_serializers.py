"""Serializers do fluxo de solicitação e assinatura hierárquica."""

from rest_framework import serializers

from atendimentos.models import SolicitacaoAssinatura
from atendimentos.setorial_serializers import SetorialOrdemServicoSerializer
from core_auth.display import nome_servidor


class SolicitarAssinaturaSerializer(serializers.Serializer):
    ordem_servico_id = serializers.UUIDField()
    assinante_destino_id = serializers.UUIDField(required=False, allow_null=True)
    despacho_tecnico = serializers.CharField(allow_blank=False, trim_whitespace=True)

    def validate_despacho_tecnico(self, value):
        texto = (value or "").strip()
        if not texto:
            raise serializers.ValidationError("O despacho técnico é obrigatório.")
        return texto


class AssinarDespachoSerializer(serializers.Serializer):
    senha_assinatura = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )


class RejeitarAssinaturaSerializer(serializers.Serializer):
    motivo_rejeicao = serializers.CharField(allow_blank=False, trim_whitespace=True)

    def validate_motivo_rejeicao(self, value):
        texto = (value or "").strip()
        if not texto:
            raise serializers.ValidationError("O motivo da rejeição é obrigatório.")
        if len(texto) < 10:
            raise serializers.ValidationError(
                "Descreva o motivo com pelo menos 10 caracteres."
            )
        return texto


class SolicitacaoAssinaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitacaoAssinatura
        fields = (
            "id",
            "ordem_servico_id",
            "solicitante_id",
            "assinante_destino_id",
            "despacho_tecnico",
            "status",
            "hash_assinatura",
            "assinada_em",
            "motivo_rejeicao",
            "rejeitada_em",
            "criado_em",
            "atualizado_em",
        )
        read_only_fields = fields


class SolicitacaoAssinaturaPendenteSerializer(SolicitacaoAssinaturaSerializer):
    ordem_servico = SetorialOrdemServicoSerializer(read_only=True)
    solicitante_nome = serializers.SerializerMethodField()
    assinante_destino_nome = serializers.SerializerMethodField()

    class Meta(SolicitacaoAssinaturaSerializer.Meta):
        fields = SolicitacaoAssinaturaSerializer.Meta.fields + (
            "ordem_servico",
            "solicitante_nome",
            "assinante_destino_nome",
        )
        read_only_fields = (
            "id",
            "ordem_servico_id",
            "solicitante_id",
            "assinante_destino_id",
            "despacho_tecnico",
            "status",
            "hash_assinatura",
            "assinada_em",
            "motivo_rejeicao",
            "rejeitada_em",
            "criado_em",
            "atualizado_em",
            "ordem_servico",
            "solicitante_nome",
            "assinante_destino_nome",
        )

    def get_solicitante_nome(self, obj):
        return nome_servidor(obj.solicitante)

    def get_assinante_destino_nome(self, obj):
        return nome_servidor(obj.assinante_destino)