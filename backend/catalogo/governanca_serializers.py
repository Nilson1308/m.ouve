"""Serializers — CRUD governança do catálogo de serviços."""

from django.utils.text import slugify
from rest_framework import serializers

from catalogo.form_builder import normalizar_formulario_schema
from catalogo.models import (
    CategoriaCatalogo,
    ServicoCatalogo,
    ServicoCatalogoVersao,
    UnidadeAdministrativa,
)
from catalogo.schema_props import validar_schema_formulario_lookup
from catalogo.versionamento_service import salvar_rascunho


class CategoriaCatalogoGovernancaSerializer(serializers.ModelSerializer):
    servicos_count = serializers.IntegerField(read_only=True, default=0)

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
            "servicos_count",
            "criado_em",
            "atualizado_em",
        )
        read_only_fields = ("id", "criado_em", "atualizado_em", "servicos_count")

    def validate_nome(self, value):
        nome = (value or "").strip()
        if len(nome) < 2:
            raise serializers.ValidationError("Informe pelo menos 2 caracteres.")
        return nome

    def validate_slug(self, value):
        slug = (value or "").strip().lower()
        if slug:
            qs = CategoriaCatalogo.objects.filter(slug=slug)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("Este slug já está em uso.")
        return slug

    def _gerar_slug(self, nome: str) -> str:
        base = slugify(nome, allow_unicode=False)[:70] or "categoria"
        candidato = base
        n = 1
        qs = CategoriaCatalogo.objects.filter(slug=candidato)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        while qs.exists():
            n += 1
            candidato = f"{base}-{n}"[:80]
            qs = CategoriaCatalogo.objects.filter(slug=candidato)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
        return candidato

    def validate(self, attrs):
        nome = attrs.get("nome") or (self.instance.nome if self.instance else "")
        slug = (attrs.get("slug") or "").strip()
        if not slug and nome:
            attrs["slug"] = self._gerar_slug(nome)
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["id"] = str(instance.id)
        return data


class ServicoCatalogoGovernancaSerializer(serializers.ModelSerializer):
    sla_padrao_horas = serializers.IntegerField(source="sla_horas", min_value=1, max_value=8760)
    categoria_id = serializers.PrimaryKeyRelatedField(
        source="categoria",
        queryset=CategoriaCatalogo.objects.all(),
        allow_null=True,
        required=False,
    )
    categoria_nome = serializers.CharField(source="categoria.nome", read_only=True, default=None)
    unidade_responsavel_id = serializers.PrimaryKeyRelatedField(
        source="unidade_responsavel",
        queryset=UnidadeAdministrativa.objects.all(),
        allow_null=True,
        required=False,
    )
    unidade_responsavel_nome = serializers.CharField(
        source="unidade_responsavel.nome",
        read_only=True,
        default=None,
    )
    executor_padrao_id = serializers.PrimaryKeyRelatedField(
        source="executor_padrao",
        queryset=UnidadeAdministrativa.objects.all(),
        allow_null=True,
        required=False,
    )
    executor_padrao_nome = serializers.CharField(
        source="executor_padrao.nome",
        read_only=True,
        default=None,
    )
    fluxo_tramitacao = serializers.ChoiceField(
        choices=ServicoCatalogo.FluxoTramitacao.choices,
        required=False,
    )
    exigir_validacao_ouvidoria = serializers.BooleanField(required=False)
    triagem_ia_ativa = serializers.BooleanField(required=False)
    exige_localizacao = serializers.BooleanField(read_only=True)
    is_template = serializers.BooleanField(read_only=True)
    tem_rascunho_pendente = serializers.BooleanField(read_only=True)
    versao_publicada = serializers.IntegerField(read_only=True)
    publicado_em = serializers.DateTimeField(read_only=True)
    salvar_como_rascunho = serializers.BooleanField(
        write_only=True,
        required=False,
        default=False,
    )

    class Meta:
        model = ServicoCatalogo
        fields = (
            "id",
            "nome",
            "descricao",
            "icone",
            "sla_padrao_horas",
            "categoria_id",
            "categoria_nome",
            "unidade_responsavel_id",
            "unidade_responsavel_nome",
            "executor_padrao_id",
            "executor_padrao_nome",
            "fluxo_tramitacao",
            "exigir_validacao_ouvidoria",
            "triagem_ia_ativa",
            "formulario_schema",
            "schema_formulario",
            "formulario_schema_rascunho",
            "schema_formulario_rascunho",
            "versao_publicada",
            "publicado_em",
            "tem_rascunho_pendente",
            "salvar_como_rascunho",
            "ativo",
            "is_template",
            "exige_localizacao",
            "permite_cluster",
            "prazo_reabertura_dias",
            "criado_em",
            "atualizado_em",
        )
        read_only_fields = (
            "id",
            "criado_em",
            "atualizado_em",
            "exige_localizacao",
            "categoria_nome",
            "unidade_responsavel_nome",
            "executor_padrao_nome",
            "is_template",
            "versao_publicada",
            "publicado_em",
            "tem_rascunho_pendente",
        )

    def validate_formulario_schema(self, value):
        try:
            return normalizar_formulario_schema(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def validate_schema_formulario(self, value):
        if value is None:
            return value
        if not isinstance(value, dict):
            raise serializers.ValidationError("schema_formulario deve ser um objeto JSON.")
        try:
            validar_schema_formulario_lookup(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return value

    def validate_fluxo_tramitacao(self, value):
        if value == "hibrido":
            raise serializers.ValidationError(
                'O fluxo "hibrido" foi descontinuado. Use "direto_secretaria" ou '
                '"ouvidoria_encaminha". Para autonomia com homologação opcional, '
                "use direto_secretaria com exigir_validacao_ouvidoria."
            )
        return value

    def validate(self, attrs):
        categoria = attrs.get("categoria")
        if self.instance and "categoria" not in attrs:
            categoria = self.instance.categoria
        if not categoria and not self.instance:
            attrs["categoria"] = CategoriaCatalogo.objects.filter(ativo=True).order_by("ordem").first()
        if not attrs.get("categoria") and not self.instance:
            raise serializers.ValidationError(
                {"categoria_id": "Informe a categoria ou cadastre uma categoria ativa."}
            )

        fluxo = attrs.get("fluxo_tramitacao")
        if fluxo is None and self.instance:
            fluxo = self.instance.fluxo_tramitacao
        unidade = attrs.get("unidade_responsavel")
        if unidade is None and self.instance and "unidade_responsavel" not in attrs:
            unidade = self.instance.unidade_responsavel
        executor = attrs.get("executor_padrao")
        if executor is None and self.instance and "executor_padrao" not in attrs:
            executor = self.instance.executor_padrao
        exigir = attrs.get("exigir_validacao_ouvidoria")
        if exigir is None and self.instance and "exigir_validacao_ouvidoria" not in attrs:
            exigir = self.instance.exigir_validacao_ouvidoria

        if fluxo == ServicoCatalogo.FluxoTramitacao.OUVIDORIA_ENCAMINHA:
            attrs["exigir_validacao_ouvidoria"] = True
            if executor is not None:
                if not executor.ativo:
                    raise serializers.ValidationError(
                        {"executor_padrao_id": "Unidade executora padrão inativa."}
                    )
        elif fluxo == ServicoCatalogo.FluxoTramitacao.DIRETO_SECRETARIA:
            attrs["executor_padrao"] = None
            if executor is not None:
                attrs["executor_padrao"] = None
            if not unidade or not unidade.ativo:
                raise serializers.ValidationError(
                    {
                        "unidade_responsavel_id": (
                            "Informe a secretaria executora ativa para o fluxo "
                            "direto_secretaria."
                        )
                    }
                )
            if exigir is None:
                attrs["exigir_validacao_ouvidoria"] = False

        return attrs

    def to_representation(self, instance):
        from catalogo.formulario_resolution import aplicar_resolucao_edicao_representation

        data = super().to_representation(instance)
        data["id"] = str(instance.id)
        data["sla_padrao_horas"] = instance.sla_horas
        data["categoria_id"] = str(instance.categoria_id) if instance.categoria_id else None
        data["unidade_responsavel_id"] = (
            str(instance.unidade_responsavel_id) if instance.unidade_responsavel_id else None
        )
        data["executor_padrao_id"] = (
            str(instance.executor_padrao_id) if instance.executor_padrao_id else None
        )
        data["tem_rascunho_pendente"] = instance.tem_rascunho_pendente
        aplicar_resolucao_edicao_representation(data, instance)
        return data

    def _extrair_schemas(self, validated_data):
        formulario = validated_data.pop("formulario_schema", serializers.empty)
        schema = validated_data.pop("schema_formulario", serializers.empty)
        return formulario, schema

    def create(self, validated_data):
        salvar_como_rascunho = validated_data.pop("salvar_como_rascunho", False)
        formulario, schema = self._extrair_schemas(validated_data)
        if salvar_como_rascunho and formulario is not serializers.empty:
            instance = super().create(validated_data)
            salvar_rascunho(
                instance,
                formulario,
                None if schema is serializers.empty else schema,
            )
            instance.refresh_from_db()
            return instance
        if formulario is not serializers.empty:
            validated_data["formulario_schema"] = formulario
        if schema is not serializers.empty:
            validated_data["schema_formulario"] = schema
        return super().create(validated_data)

    def update(self, instance, validated_data):
        salvar_como_rascunho = validated_data.pop("salvar_como_rascunho", False)
        formulario, schema = self._extrair_schemas(validated_data)

        if salvar_como_rascunho:
            if formulario is not serializers.empty or schema is not serializers.empty:
                salvar_rascunho(
                    instance,
                    formulario
                    if formulario is not serializers.empty
                    else (instance.formulario_schema_rascunho or instance.formulario_schema),
                    None if schema is serializers.empty else schema,
                )
            instance = super().update(instance, validated_data)
            instance.refresh_from_db()
            return instance

        if formulario is not serializers.empty:
            validated_data["formulario_schema"] = formulario
        if schema is not serializers.empty:
            validated_data["schema_formulario"] = schema
        return super().update(instance, validated_data)


class ServicoCatalogoPublicarSerializer(serializers.Serializer):
    nota_versao = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        max_length=255,
    )


class ServicoCatalogoVersaoSerializer(serializers.ModelSerializer):
    publicado_por_nome = serializers.CharField(
        source="publicado_por.nome",
        read_only=True,
        default=None,
    )

    class Meta:
        model = ServicoCatalogoVersao
        fields = (
            "id",
            "numero_versao",
            "nota_versao",
            "publicado_por",
            "publicado_por_nome",
            "publicado_em",
        )
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["id"] = str(instance.id)
        data["publicado_por"] = (
            str(instance.publicado_por_id) if instance.publicado_por_id else None
        )
        return data


class ServicoCatalogoClonarSerializer(serializers.Serializer):
    """
    Payload para clonar template ou duplicar serviço municipal.
    unidade_responsavel_id: obrigatório para template; opcional na duplicação (mantém a do original).
    """

    unidade_responsavel_id = serializers.PrimaryKeyRelatedField(
        queryset=UnidadeAdministrativa.objects.filter(ativo=True),
        source="unidade_responsavel",
        required=False,
        allow_null=True,
    )


class HistoricoSandboxItemSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["user", "assistant", "system"])
    content = serializers.CharField(allow_blank=True)


class ServicoCatalogoSandboxSerializer(serializers.Serializer):
    """Payload do simulador de chat (dry-run). Não grava protocolo nem sessão."""

    usar_rascunho = serializers.BooleanField(required=False, allow_null=True, default=None)
    mensagem = serializers.CharField(required=False, allow_blank=True, default="")
    dados_parciais = serializers.DictField(required=False, default=dict)
    dados_slot = serializers.DictField(required=False, allow_null=True)
    anexos_novos = serializers.IntegerField(required=False, default=0, min_value=0)
    localizacao_ok = serializers.BooleanField(required=False, default=False)
    localizacao = serializers.DictField(required=False, allow_null=True)
    historico = HistoricoSandboxItemSerializer(many=True, required=False, default=list)