from rest_framework import serializers

from catalogo.models import CategoriaCatalogo, ServicoCatalogo


class CategoriaCatalogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaCatalogo
        fields = (
            "id",
            "nome",
            "slug",
            "descricao",
            "icone",
            "ordem",
            "tipo_legado",
            "ativo",
        )
        read_only_fields = fields


class CategoriaCatalogoResumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaCatalogo
        fields = ("id", "nome", "slug", "descricao", "icone", "ordem", "tipo_legado")


class ServicoCatalogoSerializer(serializers.ModelSerializer):
    categoria = CategoriaCatalogoResumoSerializer(read_only=True)
    exige_localizacao = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServicoCatalogo
        fields = (
            "id",
            "nome",
            "descricao",
            "icone",
            "categoria",
            "sla_horas",
            "fluxo_tramitacao",
            "formulario_schema",
            "schema_formulario",
            "ativo",
            "exige_localizacao",
        )
        read_only_fields = fields


class ServicoCatalogoResumoSerializer(serializers.ModelSerializer):
    categoria = CategoriaCatalogoResumoSerializer(read_only=True)
    exige_localizacao = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServicoCatalogo
        fields = ("id", "nome", "categoria", "sla_horas", "exige_localizacao")


class ServicoCatalogoPwaSerializer(serializers.ModelSerializer):
    categoria = CategoriaCatalogoResumoSerializer(read_only=True)
    descricao_curta = serializers.SerializerMethodField()
    prazo_sla_horas = serializers.IntegerField(source="sla_horas", read_only=True)

    class Meta:
        model = ServicoCatalogo
        fields = (
            "id",
            "nome",
            "descricao_curta",
            "categoria",
            "prazo_sla_horas",
        )
        read_only_fields = fields

    def get_descricao_curta(self, obj):
        texto = (obj.descricao or "").strip()
        if len(texto) > 220:
            return texto[:217].rstrip() + "…"
        return texto
