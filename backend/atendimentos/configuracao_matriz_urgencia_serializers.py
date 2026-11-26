from rest_framework import serializers

from atendimentos.models import ConfiguracaoMatrizUrgencia


class ConfiguracaoMatrizUrgenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoMatrizUrgencia
        fields = (
            "matriz_ativa",
            "ia_urgencia_ativa",
            "ia_urgencia_modo",
            "ia_confianca_minima",
            "criterios_ia_customizados",
            "regras_campo_urgencia",
            "super_os_escalonamento_ativo",
            "super_os_limite_alta",
            "super_os_limite_critica",
            "urgencia_reduz_sla",
            "fator_sla_alta_percentual",
            "fator_sla_critica_percentual",
            "sla_minimo_critica_horas",
            "notificar_gestor_em_alta",
            "notificar_controladoria_em_critica",
            "atualizado_em",
        )
        read_only_fields = ("atualizado_em",)

    def validate_ia_confianca_minima(self, value):
        v = float(value)
        if v < 0.5 or v > 1.0:
            raise serializers.ValidationError("Deve estar entre 0,50 e 1,00.")
        return v

    def validate_super_os_limite_critica(self, value):
        limite_alta = int(
            self.initial_data.get("super_os_limite_alta")
            or getattr(self.instance, "super_os_limite_alta", 5)
        )
        if int(value) <= limite_alta:
            raise serializers.ValidationError("Deve ser maior que super_os_limite_alta.")
        return value

    def validate_super_os_limite_alta(self, value):
        if int(value) < 2:
            raise serializers.ValidationError("Mínimo 2.")
        return value

    def validate_fator_sla_alta_percentual(self, value):
        v = int(value)
        if v < 10 or v > 95:
            raise serializers.ValidationError("Entre 10 e 95.")
        return v

    def validate_fator_sla_critica_percentual(self, value):
        v = int(value)
        if v < 5 or v > 90:
            raise serializers.ValidationError("Entre 5 e 90.")
        return v

    def validate_sla_minimo_critica_horas(self, value):
        if int(value) < 1:
            raise serializers.ValidationError("Mínimo 1 hora.")
        return value