"""Serializers CRUD — equipamentos públicos (governança)."""

from rest_framework import serializers

from catalogo.equipamento_utils import (
    CoordenadasInvalidasError,
    extrair_lat_lng,
    ponto_wgs84,
)
from catalogo.models import EquipamentoPublico, UnidadeAdministrativa


class EquipamentoPublicoSerializer(serializers.ModelSerializer):
    unidade_responsavel_nome = serializers.CharField(
        source="unidade_responsavel.nome",
        read_only=True,
    )
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    georreferenciado = serializers.SerializerMethodField()

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
            "latitude",
            "longitude",
            "georreferenciado",
            "ativo",
            "criado_em",
            "atualizado_em",
        )
        read_only_fields = (
            "id",
            "criado_em",
            "atualizado_em",
            "unidade_responsavel_nome",
            "georreferenciado",
        )

    def get_georreferenciado(self, obj) -> bool:
        return obj.localizacao is not None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        lat, lng = extrair_lat_lng(instance.localizacao)
        data["latitude"] = lat
        data["longitude"] = lng
        return data

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

    def validate(self, attrs):
        lat_in = "latitude" in attrs
        lng_in = "longitude" in attrs
        if not lat_in and not lng_in:
            return attrs

        inst = getattr(self, "instance", None)
        lat = attrs["latitude"] if lat_in else None
        lng = attrs["longitude"] if lng_in else None

        if not lat_in and inst and inst.localizacao:
            lat = inst.localizacao.y
        if not lng_in and inst and inst.localizacao:
            lng = inst.localizacao.x

        if lat is None and lng is None:
            attrs.pop("latitude", None)
            attrs.pop("longitude", None)
            attrs["_limpar_localizacao"] = True
            return attrs

        if lat is None or lng is None:
            raise serializers.ValidationError(
                {
                    "latitude": (
                        "Informe latitude e longitude juntos, ou envie ambos como null "
                        "para remover a georreferência."
                    )
                }
            )

        try:
            lat_f = float(lat)
            lng_f = float(lng)
            ponto_wgs84(lat_f, lng_f)
        except (TypeError, ValueError) as exc:
            raise serializers.ValidationError(
                {"latitude": "Coordenadas devem ser numéricas."}
            ) from exc
        except CoordenadasInvalidasError as exc:
            raise serializers.ValidationError(
                {"latitude": str(exc), "longitude": str(exc)}
            ) from exc

        attrs["latitude"] = lat_f
        attrs["longitude"] = lng_f
        attrs["_coords_localizacao"] = (lat_f, lng_f)
        return attrs

    def _extrair_geo_da_validacao(self, validated_data):
        limpar = validated_data.pop("_limpar_localizacao", False)
        coords = validated_data.pop("_coords_localizacao", None)
        validated_data.pop("latitude", None)
        validated_data.pop("longitude", None)
        return limpar, coords

    def create(self, validated_data):
        limpar, coords = self._extrair_geo_da_validacao(validated_data)
        if limpar:
            validated_data["localizacao"] = None
        elif coords:
            lat, lng = coords
            validated_data["localizacao"] = ponto_wgs84(lat, lng)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        limpar, coords = self._extrair_geo_da_validacao(validated_data)
        if limpar:
            instance.localizacao = None
        elif coords:
            lat, lng = coords
            instance.localizacao = ponto_wgs84(lat, lng)
        return super().update(instance, validated_data)