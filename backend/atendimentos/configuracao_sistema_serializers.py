from rest_framework import serializers

from atendimentos.models import ConfiguracaoSistema


class ConfiguracaoSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoSistema
        fields = (
            "modo_abertura_pwa",
            "dias_busca_cluster_ia",
            "notificar_novos_despachos",
            "notificar_sla_vencido",
            "notificar_novas_super_os",
            "atualizado_em",
        )
        read_only_fields = ("atualizado_em",)