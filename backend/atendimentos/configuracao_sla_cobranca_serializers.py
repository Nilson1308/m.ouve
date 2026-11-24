"""Serializers — ConfiguracaoSlaCobranca."""

from rest_framework import serializers

from atendimentos.models import ConfiguracaoSlaCobranca


def _validar_emails(valores) -> list:
    if not isinstance(valores, list):
        raise serializers.ValidationError("Deve ser uma lista de e-mails.")
    out: list[str] = []
    for e in valores:
        if not isinstance(e, str) or "@" not in e.strip():
            raise serializers.ValidationError(f"E-mail inválido: {e!r}")
        out.append(e.strip().lower())
    return out


class ConfiguracaoSlaCobrancaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoSlaCobranca
        fields = (
            "cobranca_cidadao_ativa",
            "cooldown_cobranca_horas",
            "alerta_preventivo_percentual",
            "escalonamento_controladoria_dias",
            "emails_controladoria",
            "digest_email_ativo",
            "digest_periodicidade",
            "digest_hora_envio",
            "atualizado_em",
        )
        read_only_fields = ("atualizado_em",)

    def validate_alerta_preventivo_percentual(self, value):
        if value < 50 or value > 99:
            raise serializers.ValidationError("Informe um percentual entre 50 e 99.")
        return value

    def validate_digest_hora_envio(self, value):
        if value < 0 or value > 23:
            raise serializers.ValidationError("Hora deve estar entre 0 e 23.")
        return value

    def validate_emails_controladoria(self, value):
        return _validar_emails(value)