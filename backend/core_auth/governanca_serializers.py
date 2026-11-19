"""Serializers CRUD de governança (unidades, usuários e perfis de acesso)."""

import secrets
import string

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from catalogo.models import UnidadeAdministrativa
from core_auth.models import PerfilAcesso, Usuario
from core_auth.rbac import (
    aplicar_regras_automaticas,
    normalizar_permissoes,
    perfil_exige_unidade,
    permissoes_padrao,
    permissoes_para_matriz_ui,
)
from core_auth.utils import normalizar_cpf


def gerar_senha_aleatoria(tamanho: int = 14) -> str:
    alfabeto = string.ascii_letters + string.digits
    return "".join(secrets.choice(alfabeto) for _ in range(tamanho))


class PerfilAcessoSerializer(serializers.ModelSerializer):
    qtd_usuarios = serializers.IntegerField(read_only=True, required=False)
    usuarios_count = serializers.SerializerMethodField()
    slug = serializers.CharField(required=False, allow_blank=True)
    requer_vinculo = serializers.BooleanField(required=False)
    permissoes = serializers.JSONField()

    class Meta:
        model = PerfilAcesso
        fields = (
            "id",
            "codigo",
            "slug",
            "nome",
            "descricao",
            "permissoes",
            "requer_vinculo",
            "ativo",
            "sistema",
            "qtd_usuarios",
            "usuarios_count",
            "criado_em",
            "atualizado_em",
        )
        read_only_fields = (
            "id",
            "criado_em",
            "atualizado_em",
            "sistema",
            "qtd_usuarios",
            "usuarios_count",
        )

    def get_usuarios_count(self, obj):
        return getattr(obj, "qtd_usuarios", 0)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["id"] = str(instance.id)
        data["slug"] = instance.codigo or ""
        data["codigo"] = instance.codigo or ""
        data["permissoes"] = permissoes_para_matriz_ui(instance)
        data["requer_vinculo"] = perfil_exige_unidade(instance)
        return data

    def _resolver_codigo(self, validated_data):
        slug = (validated_data.pop("slug", None) or validated_data.get("codigo") or "").strip()
        if slug:
            return str(slug).lower().replace(" ", "_")
        from django.utils.text import slugify

        base = slugify(validated_data.get("nome", ""))[:40] or "perfil"
        return f"{base}_{secrets.token_hex(3)}"

    def _montar_permissoes(self, validated_data, instance=None):
        requer = validated_data.pop("requer_vinculo", None)
        entrada = validated_data.get("permissoes") or {}
        codigo = validated_data.get("codigo") or (instance.codigo if instance else "")
        preservar_super = False
        if instance:
            from core_auth.rbac import regras_do_perfil

            preservar_super = bool(regras_do_perfil(instance).get("super_admin"))
        return aplicar_regras_automaticas(
            entrada,
            requer_vinculo=requer,
            codigo=codigo,
            preservar_super_admin=preservar_super,
        )

    def create(self, validated_data):
        validated_data["codigo"] = self._resolver_codigo(validated_data)
        validated_data["permissoes"] = self._montar_permissoes(validated_data)
        if validated_data.get("ativo") is None:
            validated_data["ativo"] = True
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "slug" in validated_data or "codigo" in validated_data:
            instance.codigo = self._resolver_codigo(
                {**validated_data, "nome": validated_data.get("nome", instance.nome)}
            )
        if "permissoes" in validated_data or "requer_vinculo" in self.initial_data:
            instance.permissoes = self._montar_permissoes(
                {**validated_data, "codigo": instance.codigo},
                instance=instance,
            )
        for campo in ("nome", "descricao", "ativo"):
            if campo in validated_data:
                setattr(instance, campo, validated_data[campo])
        instance.save()
        return instance


class UnidadeAdministrativaGovernancaSerializer(serializers.ModelSerializer):
    qtd_usuarios = serializers.IntegerField(read_only=True)
    usuarios_count = serializers.SerializerMethodField()
    tom_ia_display = serializers.CharField(source="get_tom_ia_display", read_only=True)

    class Meta:
        model = UnidadeAdministrativa
        fields = (
            "id",
            "nome",
            "sigla",
            "descricao",
            "tom_ia",
            "tom_ia_display",
            "diretrizes_tom_ia",
            "ativo",
            "qtd_usuarios",
            "usuarios_count",
            "criado_em",
            "atualizado_em",
        )
        read_only_fields = (
            "id",
            "criado_em",
            "atualizado_em",
            "qtd_usuarios",
            "usuarios_count",
            "tom_ia_display",
        )

    def get_usuarios_count(self, obj):
        return getattr(obj, "qtd_usuarios", 0)

    def validate_diretrizes_tom_ia(self, value):
        texto = (value or "").strip()
        if len(texto) > 500:
            raise serializers.ValidationError(
                "Diretrizes de tom devem ter no máximo 500 caracteres."
            )
        return texto

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["id"] = str(instance.id)
        return data


def resolver_perfil_acesso(*, perfil_acesso_id=None, perfil=None, perfil_codigo=None):
    """Resolve FK por UUID, id do Vue ou slug/código."""
    chave = perfil_acesso_id or perfil_codigo or perfil
    if chave is None or chave == "":
        raise serializers.ValidationError("Informe perfil_acesso_id ou perfil.")
    texto = str(chave).strip()
    try:
        return PerfilAcesso.objects.get(pk=texto)
    except (PerfilAcesso.DoesNotExist, ValueError, TypeError):
        pass
    codigo = texto.lower()
    obj = PerfilAcesso.objects.filter(codigo=codigo).first()
    if not obj:
        raise serializers.ValidationError(f"Perfil de acesso não encontrado: {texto}")
    return obj


class UsuarioGovernancaSerializer(serializers.ModelSerializer):
    perfil_acesso_id = serializers.PrimaryKeyRelatedField(
        source="perfil_acesso",
        queryset=PerfilAcesso.objects.all(),
        allow_null=True,
        required=False,
    )
    perfil_acesso_nome = serializers.CharField(source="perfil_acesso.nome", read_only=True, default=None)
    perfil = serializers.CharField(source="perfil_acesso.codigo", read_only=True, default=None)
    perfil_codigo = serializers.CharField(write_only=True, required=False, allow_blank=True)
    unidade_id = serializers.PrimaryKeyRelatedField(
        source="unidade",
        queryset=UnidadeAdministrativa.objects.all(),
        allow_null=True,
        required=False,
    )
    unidade_nome = serializers.CharField(source="unidade.nome", read_only=True, default=None)
    ativo = serializers.BooleanField(source="is_active")
    criado_em = serializers.DateTimeField(source="created_at", read_only=True)
    atualizado_em = serializers.DateTimeField(source="updated_at", read_only=True)
    ultimo_acesso = serializers.DateTimeField(source="last_login", read_only=True)

    class Meta:
        model = Usuario
        fields = (
            "id",
            "nome",
            "email",
            "cpf",
            "perfil",
            "perfil_acesso_id",
            "perfil_acesso_nome",
            "perfil_codigo",
            "unidade_id",
            "unidade_nome",
            "ativo",
            "ultimo_acesso",
            "criado_em",
            "atualizado_em",
        )
        read_only_fields = (
            "id",
            "perfil",
            "perfil_acesso_nome",
            "criado_em",
            "atualizado_em",
            "ultimo_acesso",
            "unidade_nome",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["perfil_acesso_id"] = (
            str(instance.perfil_acesso_id) if instance.perfil_acesso_id else None
        )
        data["unidade_id"] = str(instance.unidade_id) if instance.unidade_id else None
        data["id"] = str(instance.id)
        data["cpf"] = self._formatar_cpf_exibicao(instance.cpf)
        data["perfil"] = instance.perfil_acesso.codigo if instance.perfil_acesso_id else ""
        data["perfil_acesso_nome"] = (
            instance.perfil_acesso.nome if instance.perfil_acesso_id else None
        )
        return data

    def _formatar_cpf_exibicao(self, cpf: str) -> str:
        digits = normalizar_cpf(cpf)
        if len(digits) != 11:
            return cpf
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"

    def validate_cpf(self, value):
        cpf = normalizar_cpf(value)
        if len(cpf) != 11:
            raise serializers.ValidationError("CPF inválido.")
        return cpf

    def validate(self, attrs):
        perfil_acesso = attrs.get("perfil_acesso")
        if perfil_acesso is None:
            bruto = (
                self.initial_data.get("perfil_acesso_id")
                or self.initial_data.get("perfil")
                or self.initial_data.get("perfil_codigo")
            )
            if bruto:
                perfil_acesso = resolver_perfil_acesso(perfil_acesso_id=bruto, perfil=bruto)
                attrs["perfil_acesso"] = perfil_acesso
        if perfil_acesso is None and self.instance:
            perfil_acesso = self.instance.perfil_acesso
        if perfil_acesso is None:
            raise serializers.ValidationError(
                {"perfil_acesso_id": "Perfil de acesso é obrigatório para servidores."}
            )

        unidade = attrs.get("unidade")
        if "unidade" not in attrs and self.instance:
            unidade = self.instance.unidade

        if perfil_exige_unidade(perfil_acesso) and not unidade:
            raise serializers.ValidationError(
                {"unidade_id": "Unidade é obrigatória para este perfil de acesso."}
            )
        if not perfil_exige_unidade(perfil_acesso) and unidade:
            raise serializers.ValidationError(
                {"unidade_id": "Este perfil de acesso não aceita vínculo com unidade."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("perfil_codigo", None)
        if "perfil_acesso" not in validated_data and self.initial_data:
            validated_data["perfil_acesso"] = resolver_perfil_acesso(
                perfil_acesso_id=self.initial_data.get("perfil_acesso_id"),
                perfil=self.initial_data.get("perfil"),
                perfil_codigo=self.initial_data.get("perfil_codigo"),
            )
        senha = self.context.get("senha_inicial") or gerar_senha_aleatoria()
        usuario = Usuario(
            nome=validated_data["nome"],
            email=validated_data["email"],
            cpf=validated_data["cpf"],
            perfil_acesso=validated_data["perfil_acesso"],
            unidade=validated_data.get("unidade"),
            is_active=validated_data.get("is_active", True),
        )
        usuario.set_password(senha)
        try:
            usuario.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else str(exc)
            )
        self.context["senha_gerada"] = senha
        return usuario

    def update(self, instance, validated_data):
        validated_data.pop("perfil_codigo", None)
        if "perfil_acesso" not in validated_data and self.initial_data.get("perfil"):
            validated_data["perfil_acesso"] = resolver_perfil_acesso(
                perfil=self.initial_data.get("perfil"),
                perfil_codigo=self.initial_data.get("perfil_codigo"),
            )
        for field in ("nome", "email", "cpf", "perfil_acesso", "unidade", "is_active"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        try:
            instance.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else str(exc)
            )
        return instance


class UsuarioGovernancaCreateSerializer(UsuarioGovernancaSerializer):
    senha = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=8)

    class Meta(UsuarioGovernancaSerializer.Meta):
        fields = UsuarioGovernancaSerializer.Meta.fields + ("senha",)

    def validate(self, attrs):
        if "perfil_acesso" not in attrs:
            try:
                attrs["perfil_acesso"] = resolver_perfil_acesso(
                    perfil_acesso_id=self.initial_data.get("perfil_acesso_id"),
                    perfil=self.initial_data.get("perfil"),
                    perfil_codigo=self.initial_data.get("perfil_codigo"),
                )
            except serializers.ValidationError as exc:
                raise serializers.ValidationError({"perfil_acesso_id": exc.detail})
        return super().validate(attrs)

    def create(self, validated_data):
        senha = (validated_data.pop("senha", None) or "").strip() or None
        self.context["senha_inicial"] = senha
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        senha = self.context.get("senha_gerada")
        if senha:
            data["senha_inicial"] = senha
        return data


class ResetarSenhaResponseSerializer(serializers.Serializer):
    sucesso = serializers.BooleanField()
    mensagem = serializers.CharField()
    usuario_id = serializers.UUIDField()
    senha = serializers.CharField()
    email = serializers.EmailField()