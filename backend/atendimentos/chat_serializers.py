"""Serializers da API de chat conversacional."""

import json

from rest_framework import serializers

from atendimentos.chat_estado import get_fase, get_pending_escolha
from atendimentos.chat_resumo import montar_resumo_revisao
from atendimentos.models import MensagemChat, SessaoChat
from catalogo.serializers import ServicoCatalogoResumoSerializer


class MensagemChatSerializer(serializers.ModelSerializer):
    localizacao = serializers.SerializerMethodField()
    fotos = serializers.SerializerMethodField()

    class Meta:
        model = MensagemChat
        fields = (
            "id",
            "autor",
            "conteudo_texto",
            "localizacao",
            "tipo_acao",
            "payload_ui",
            "fotos",
            "criado_em",
        )

    def get_localizacao(self, obj):
        if not obj.localizacao:
            return None
        return {"latitude": obj.localizacao.y, "longitude": obj.localizacao.x}

    def get_fotos(self, obj):
        from ouvia_core.url_utils import public_absolute_uri

        request = self.context.get("request")
        fotos = []
        for anexo in obj.anexos.all().order_by("criado_em"):
            if not (anexo.tipo_mime or "").startswith("image/"):
                continue
            url = public_absolute_uri(request, anexo.arquivo.url if anexo.arquivo else None)
            if not url:
                continue
            fotos.append(
                {
                    "url": url,
                    "nome": anexo.nome_original or "foto.jpg",
                }
            )
        return fotos


class SessaoChatSerializer(serializers.ModelSerializer):
    servico_identificado = ServicoCatalogoResumoSerializer(read_only=True)
    protocolo_final_id = serializers.UUIDField(read_only=True, allow_null=True)
    fase = serializers.SerializerMethodField()
    total_anexos = serializers.SerializerMethodField()
    resumo_revisao = serializers.SerializerMethodField()
    pending_escolha = serializers.SerializerMethodField()

    class Meta:
        model = SessaoChat
        fields = (
            "id",
            "categoria_inicial",
            "status",
            "fase",
            "origem_abertura",
            "servico_identificado",
            "dados_coletados",
            "pending_escolha",
            "resumo_revisao",
            "protocolo_final_id",
            "total_anexos",
            "criado_em",
            "atualizado_em",
        )

    def get_fase(self, obj):
        return get_fase(obj)

    def get_total_anexos(self, obj):
        return obj.anexos_sessao.count()

    def get_resumo_revisao(self, obj):
        request = self.context.get("request")
        return montar_resumo_revisao(obj, request=request)

    def get_pending_escolha(self, obj):
        return get_pending_escolha(obj)


class AvaliarAberturaChatSerializer(serializers.Serializer):
    """Pesquisa pós-protocolo no chat — experiência de abertura, não CSAT de resolução."""

    nota = serializers.IntegerField(min_value=1, max_value=5)
    comentario = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate(self, attrs):
        sessao = self.context.get("sessao")
        if sessao is None:
            raise serializers.ValidationError({"detail": "Sessão não encontrada."})
        if sessao.status != SessaoChat.Status.FINALIZADO_PROTOCOLO:
            raise serializers.ValidationError(
                {
                    "sessao": (
                        "Avaliação disponível apenas após registrar o protocolo nesta conversa."
                    )
                }
            )
        if not sessao.protocolo_final_id:
            raise serializers.ValidationError(
                {"sessao": "Nenhum protocolo vinculado a esta sessão."}
            )
        if sessao.nota_abertura is not None:
            raise serializers.ValidationError(
                {"sessao": "Esta abertura já foi avaliada."}
            )
        return attrs

    def save(self, **kwargs):
        from django.utils import timezone

        sessao = self.context["sessao"]
        comentario = (self.validated_data.get("comentario") or "").strip()
        sessao.nota_abertura = self.validated_data["nota"]
        sessao.comentario_abertura = comentario
        sessao.avaliacao_abertura_em = timezone.now()
        sessao.save(
            update_fields=[
                "nota_abertura",
                "comentario_abertura",
                "avaliacao_abertura_em",
                "atualizado_em",
            ]
        )
        return sessao


class CriarSessaoChatSerializer(serializers.Serializer):
    categoria_inicial = serializers.CharField(max_length=80)
    servico_id = serializers.UUIDField(required=False, allow_null=True)


class InteragirChatSerializer(serializers.Serializer):
    sessao_id = serializers.UUIDField()
    texto = serializers.CharField(required=False, allow_blank=True, default="")
    localizacao = serializers.JSONField(required=False, allow_null=True)
    confirmar_protocolo = serializers.BooleanField(required=False, default=False)
    dados_slot = serializers.JSONField(required=False, allow_null=True)

    def to_internal_value(self, data):
        if hasattr(data, "copy"):
            payload = data.copy()
        else:
            payload = dict(data)

        raw_loc = payload.get("localizacao")
        if isinstance(raw_loc, str) and raw_loc.strip():
            try:
                payload["localizacao"] = json.loads(raw_loc)
            except json.JSONDecodeError as exc:
                raise serializers.ValidationError(
                    {"localizacao": "JSON inválido. Envie objeto ou string JSON."}
                ) from exc
        elif isinstance(raw_loc, str):
            payload["localizacao"] = None

        raw_slot = payload.get("dados_slot")
        if isinstance(raw_slot, str) and raw_slot.strip():
            try:
                payload["dados_slot"] = json.loads(raw_slot)
            except json.JSONDecodeError as exc:
                raise serializers.ValidationError(
                    {"dados_slot": "JSON inválido."}
                ) from exc

        return super().to_internal_value(payload)

    def validate_sessao_id(self, value):
        request = self.context["request"]
        try:
            sessao = SessaoChat.objects.get(pk=value, usuario=request.user)
        except SessaoChat.DoesNotExist as exc:
            raise serializers.ValidationError("Sessão não encontrada.") from exc
        if sessao.status != SessaoChat.Status.EM_ANDAMENTO:
            raise serializers.ValidationError("Esta sessão não aceita novas mensagens.")
        self.context["sessao"] = sessao
        return value

    def validate_localizacao(self, value):
        if value is None:
            return None
        if not isinstance(value, dict):
            raise serializers.ValidationError("localizacao deve ser um objeto.")
        lat = value.get("latitude")
        lng = value.get("longitude")
        if lat is None or lng is None:
            raise serializers.ValidationError("localizacao deve conter latitude e longitude.")
        return value
