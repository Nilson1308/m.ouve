from rest_framework import serializers

from atendimentos.models import NotificacaoInterna


class NotificacaoInternaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificacaoInterna
        fields = (
            "id",
            "titulo",
            "mensagem",
            "lida",
            "link_acao",
            "data_criacao",
        )
        read_only_fields = fields
