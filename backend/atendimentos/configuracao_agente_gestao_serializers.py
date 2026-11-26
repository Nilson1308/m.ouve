"""Serializers — ConfiguracaoAgenteGestao."""

from rest_framework import serializers

from atendimentos.models import ConfiguracaoAgenteGestao


class ConfiguracaoAgenteGestaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoAgenteGestao
        fields = (
            "agente_ativo",
            "briefing_proativo_ativo",
            "briefing_hora_geracao",
            "incluir_resumo_no_digest_email",
            "copiloto_chat_ativo",
            "limite_perguntas_dia_por_usuario",
            "orcamento_tokens_mensal",
            "anomalia_percentual_minimo",
            "anomalia_volume_minimo",
            "dias_parado_triagem_alerta",
            "atualizado_em",
        )
        read_only_fields = ("atualizado_em",)

    def validate_briefing_hora_geracao(self, value):
        v = int(value)
        if v < 0 or v > 23:
            raise serializers.ValidationError("Hora deve estar entre 0 e 23.")
        return v

    def validate_limite_perguntas_dia_por_usuario(self, value):
        if int(value) < 1:
            raise serializers.ValidationError("Mínimo 1.")
        return value

    def validate_orcamento_tokens_mensal(self, value):
        if int(value) < 10_000:
            raise serializers.ValidationError("Mínimo 10.000 tokens.")
        return value

    def validate_anomalia_percentual_minimo(self, value):
        v = int(value)
        if v < 10 or v > 500:
            raise serializers.ValidationError("Deve estar entre 10 e 500.")
        return v

    def validate_anomalia_volume_minimo(self, value):
        if int(value) < 2:
            raise serializers.ValidationError("Mínimo 2.")
        return value

    def validate_dias_parado_triagem_alerta(self, value):
        if int(value) < 1:
            raise serializers.ValidationError("Mínimo 1.")
        return value