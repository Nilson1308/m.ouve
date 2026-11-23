"""Serializers — CRUD da matriz de roteamento temático (governança)."""

from django.db import IntegrityError
from rest_framework import serializers

from catalogo.models import MatrizRoteamentoTematico, UnidadeAdministrativa


class MatrizRoteamentoTematicoSerializer(serializers.ModelSerializer):
    unidade_sugerida = serializers.PrimaryKeyRelatedField(
        queryset=UnidadeAdministrativa.objects.filter(ativo=True)
    )
    unidade_sugerida_nome = serializers.CharField(
        source="unidade_sugerida.nome", read_only=True
    )

    class Meta:
        model = MatrizRoteamentoTematico
        fields = (
            "id",
            "chave_schema",
            "valor_condicao",
            "unidade_sugerida",
            "unidade_sugerida_nome",
            "ativo",
            "criado_em",
            "atualizado_em",
        )
        read_only_fields = ("id", "criado_em", "atualizado_em", "unidade_sugerida_nome")

    def validate_chave_schema(self, value):
        chave = (value or "").strip()
        if not chave:
            raise serializers.ValidationError("Informe a chave do campo no schema.")
        if len(chave) > 80:
            raise serializers.ValidationError("Chave excede 80 caracteres.")
        return chave

    def validate_valor_condicao(self, value):
        val = (value or "").strip()
        if not val:
            raise serializers.ValidationError("Informe o valor da condição.")
        if len(val) > 120:
            raise serializers.ValidationError("Valor excede 120 caracteres.")
        return val

    def validate_unidade_sugerida(self, value):
        if not isinstance(value, UnidadeAdministrativa):
            return value
        if not value.ativo:
            raise serializers.ValidationError(
                "A unidade sugerida precisa estar ativa."
            )
        return value

    def _mensagem_duplicidade(self):
        return (
            "Já existe uma regra para este serviço com a mesma "
            "chave_schema e valor_condicao."
        )

    def validate(self, attrs):
        unidade = attrs.get("unidade_sugerida")
        if unidade is None and self.instance:
            unidade = self.instance.unidade_sugerida
        if unidade and not unidade.ativo:
            raise serializers.ValidationError(
                {"unidade_sugerida": "A unidade sugerida precisa estar ativa."}
            )

        chave = attrs.get("chave_schema")
        if chave is None and self.instance:
            chave = self.instance.chave_schema
        valor = attrs.get("valor_condicao")
        if valor is None and self.instance:
            valor = self.instance.valor_condicao

        servico = self.context.get("servico")
        if servico and chave is not None and valor is not None:
            qs = MatrizRoteamentoTematico.objects.filter(
                servico=servico,
                chave_schema=chave,
                valor_condicao=valor,
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"detail": self._mensagem_duplicidade()})

        return attrs

    def create(self, validated_data):
        servico = self.context["servico"]
        try:
            return MatrizRoteamentoTematico.objects.create(
                servico=servico, **validated_data
            )
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Já existe uma regra para este serviço com a mesma "
                        "chave_schema e valor_condicao."
                    )
                }
            ) from exc

    def update(self, instance, validated_data):
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        try:
            instance.save()
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Já existe uma regra para este serviço com a mesma "
                        "chave_schema e valor_condicao."
                    )
                }
            ) from exc
        return instance