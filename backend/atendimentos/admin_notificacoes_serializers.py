"""Serializers — auditoria e broadcast de notificações internas (Super Admin)."""

from rest_framework import serializers

from atendimentos.models import NotificacaoInterna


class NotificacaoInternaAuditoriaSerializer(serializers.ModelSerializer):
    usuario_destino_id = serializers.UUIDField(read_only=True)
    usuario_destino_nome = serializers.CharField(source="usuario_destino.nome", read_only=True)
    usuario_destino_email = serializers.EmailField(
        source="usuario_destino.email",
        read_only=True,
    )
    unidade_destino_id = serializers.SerializerMethodField()
    unidade_destino_nome = serializers.SerializerMethodField()

    class Meta:
        model = NotificacaoInterna
        fields = (
            "id",
            "titulo",
            "mensagem",
            "lida",
            "link_acao",
            "data_criacao",
            "usuario_destino_id",
            "usuario_destino_nome",
            "usuario_destino_email",
            "unidade_destino_id",
            "unidade_destino_nome",
        )
        read_only_fields = fields

    def get_unidade_destino_id(self, obj):
        unidade = getattr(obj.usuario_destino, "unidade", None)
        return str(unidade.id) if unidade else None

    def get_unidade_destino_nome(self, obj):
        unidade = getattr(obj.usuario_destino, "unidade", None)
        if not unidade:
            return None
        return unidade.nome


class NotificacaoBroadcastSerializer(serializers.Serializer):
    titulo = serializers.CharField(max_length=255)
    mensagem = serializers.CharField()
    unidade_alvo_id = serializers.UUIDField(required=False, allow_null=True)
    nivel_urgencia = serializers.ChoiceField(
        choices=("normal", "alta"),
        default="normal",
    )