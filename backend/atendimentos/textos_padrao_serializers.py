from rest_framework import serializers

from atendimentos.models import TextoPadraoDespacho


class TextoPadraoDespachoSerializer(serializers.ModelSerializer):
    unidade_nome = serializers.CharField(source="unidade.nome", read_only=True)
    unidade_sigla = serializers.CharField(source="unidade.sigla", read_only=True)

    class Meta:
        model = TextoPadraoDespacho
        fields = (
            "id",
            "unidade",
            "unidade_nome",
            "unidade_sigla",
            "titulo",
            "texto",
            "ativo",
            "criado_em",
            "atualizado_em",
        )
        read_only_fields = ("id", "unidade", "criado_em", "atualizado_em")

    def validate_titulo(self, value):
        titulo = (value or "").strip()
        if not titulo:
            raise serializers.ValidationError("Título é obrigatório.")
        return titulo

    def validate_texto(self, value):
        texto = (value or "").strip()
        if not texto:
            raise serializers.ValidationError("Texto do despacho é obrigatório.")
        return texto
