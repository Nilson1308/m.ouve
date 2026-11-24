"""Serializers de avaliação de protocolo (CSAT — PWA cidadão)."""

from rest_framework import serializers

from atendimentos.models import AvaliacaoProtocolo, Protocolo


class _BaseAvaliacaoSerializer(serializers.Serializer):
    nota = serializers.IntegerField(min_value=1, max_value=5)
    comentario = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def _protocolo_do_contexto(self) -> Protocolo:
        protocolo = self.context.get("protocolo")
        if protocolo is None:
            raise serializers.ValidationError({"detail": "Protocolo não encontrado."})
        return protocolo

    def validate(self, attrs):
        request = self.context["request"]
        protocolo = self._protocolo_do_contexto()
        if protocolo.usuario_id != request.user.id:
            raise serializers.ValidationError(
                {"protocolo_id": "Protocolo não encontrado."}
            )
        if protocolo.status != Protocolo.Status.RESOLVIDO:
            raise serializers.ValidationError(
                {
                    "protocolo_id": (
                        "Só é possível avaliar protocolos concluídos (status resolvido)."
                    )
                }
            )
        av_existente = AvaliacaoProtocolo.objects.filter(protocolo=protocolo).first()
        if av_existente:
            permite_nova = (
                protocolo.ultima_reabertura_em
                and av_existente.criada_em < protocolo.ultima_reabertura_em
            )
            if not permite_nova:
                raise serializers.ValidationError(
                    {"protocolo_id": "Este protocolo já foi avaliado."}
                )
        return attrs

    def create(self, validated_data):
        protocolo = self._protocolo_do_contexto()
        comentario = (validated_data.get("comentario") or "").strip()
        av_existente = AvaliacaoProtocolo.objects.filter(protocolo=protocolo).first()
        if av_existente:
            av_existente.nota = validated_data["nota"]
            av_existente.comentario = comentario
            av_existente.save(update_fields=["nota", "comentario"])
            avaliacao = av_existente
        else:
            avaliacao = AvaliacaoProtocolo.objects.create(
                protocolo=protocolo,
                nota=validated_data["nota"],
                comentario=comentario,
            )
        protocolo.nota_satisfacao = validated_data["nota"]
        protocolo.comentario_satisfacao = comentario or None
        protocolo.save(update_fields=["nota_satisfacao", "comentario_satisfacao"])
        return avaliacao


class AvaliacaoProtocoloSerializer(_BaseAvaliacaoSerializer):
    """Legado — body com ``protocolo_id``."""

    protocolo_id = serializers.UUIDField()

    def validate_protocolo_id(self, value):
        request = self.context["request"]
        try:
            protocolo = Protocolo.objects.get(pk=value, usuario=request.user)
        except Protocolo.DoesNotExist as exc:
            raise serializers.ValidationError("Protocolo não encontrado.") from exc
        self.context["protocolo"] = protocolo
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        return attrs

    def to_representation(self, instance):
        if isinstance(instance, AvaliacaoProtocolo):
            return {
                "id": str(instance.id),
                "protocolo_id": str(instance.protocolo_id),
                "nota": instance.nota,
                "comentario": instance.comentario,
                "criada_em": instance.criada_em,
            }
        return super().to_representation(instance)


class AvaliarProtocoloAppSerializer(_BaseAvaliacaoSerializer):
    """Payload ``{ nota, comentario? }`` — protocolo vem da URL."""