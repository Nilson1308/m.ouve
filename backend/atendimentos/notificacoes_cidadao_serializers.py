"""Serializers — notificações do cidadão (PWA)."""

from rest_framework import serializers

from atendimentos.models import NotificacaoCidadao, PushSubscription


class NotificacaoCidadaoSerializer(serializers.ModelSerializer):
    protocolo_id = serializers.SerializerMethodField()
    protocolo_codigo = serializers.SerializerMethodField()

    class Meta:
        model = NotificacaoCidadao
        fields = (
            "id",
            "titulo",
            "mensagem",
            "lida",
            "criada_em",
            "protocolo_id",
            "protocolo_codigo",
        )
        read_only_fields = fields

    def get_protocolo_id(self, obj):
        return str(obj.protocolo_id) if obj.protocolo_id else None

    def get_protocolo_codigo(self, obj):
        if obj.protocolo_id and getattr(obj, "protocolo", None):
            return obj.protocolo.codigo
        return None


class PushSubscribeSerializer(serializers.Serializer):
    endpoint = serializers.URLField(max_length=1024)
    keys = serializers.DictField(child=serializers.CharField(), required=False)
    p256dh = serializers.CharField(required=False, allow_blank=True)
    auth = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        keys = attrs.get("keys") or {}
        p256dh = (attrs.get("p256dh") or keys.get("p256dh") or "").strip()
        auth = (attrs.get("auth") or keys.get("auth") or "").strip()
        if not p256dh or not auth:
            raise serializers.ValidationError(
                {"keys": "Informe keys.p256dh e keys.auth (formato Web Push do navegador)."}
            )
        attrs["p256dh"] = p256dh
        attrs["auth"] = auth
        return attrs

    def save(self, usuario):
        endpoint = self.validated_data["endpoint"]
        sub, _created = PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                "usuario": usuario,
                "p256dh": self.validated_data["p256dh"],
                "auth": self.validated_data["auth"],
            },
        )
        return sub


class PushSubscriptionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = ("id", "endpoint", "criada_em", "atualizado_em")
        read_only_fields = fields