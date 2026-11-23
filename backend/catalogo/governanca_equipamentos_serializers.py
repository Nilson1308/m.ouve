"""Serializers CRUD — equipamentos públicos (governança)."""

from rest_framework import serializers

from catalogo.models import EquipamentoPublico, UnidadeAdministrativa


class EquipamentoPublicoSerializer(serializers.ModelSerializer):
    unidade_responsavel_nome = serializers.CharField(
        source="unidade_responsavel.nome",
        read_only=True,
    )

    class Meta:
        model = EquipamentoPublico
        fields = (
            "id",
            "nome",
            "tipo",
            "unidade_responsavel",
            "unidade_responsavel_nome",
            "apelidos",
            "endereco",
            "bairro",
            "ativo",
            "criado_em",
            "atualizado_em",
        )
        read_only_fields = ("id", "criado_em", "atualizado_em", "unidade_responsavel_nome")

    def validate_unidade_responsavel(self, value):
        if not value or not value.ativo:
            raise serializers.ValidationError(
                "Selecione uma unidade administrativa ativa."
            )
        return value

    def validate_apelidos(self, value):
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("Apelidos deve ser uma lista de textos.")
        limpos: list[str] = []
        for item in value:
            if item is None:
                continue
            texto = str(item).strip()
            if texto and texto not in limpos:
                limpos.append(texto)
        return limpos