"""Serializers de autenticação e perfil."""

from django.contrib.auth.password_validation import validate_password
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from core_auth.models import DispositivoPush, EnderecoCidadao, Notificacao, Usuario
from core_auth.rbac import listar_permissoes_efetivas, usuario_e_backoffice, usuario_e_cidadao, usuario_e_super_admin
from core_auth.utils import cpf_valido, formatar_cpf, normalizar_cpf


class CoordenadasSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    precisao = serializers.ChoiceField(
        choices=["exata", "rua", "cidade"], required=False, default="cidade"
    )


class EnderecoSerializer(serializers.Serializer):
    cep = serializers.CharField(max_length=9)
    logradouro = serializers.CharField(max_length=255)
    numero = serializers.CharField(max_length=20, required=False, allow_blank=True)
    complemento = serializers.CharField(max_length=120, required=False, allow_blank=True)
    bairro = serializers.CharField(max_length=120)
    cidade = serializers.CharField(max_length=120)
    estado = serializers.CharField(max_length=2)
    coordenadas = CoordenadasSerializer(required=False)


class UsuarioResponseSerializer(serializers.ModelSerializer):
    """Representação pública do usuário no contrato da API."""

    cpf = serializers.SerializerMethodField()
    endereco = serializers.SerializerMethodField()
    perfil = serializers.SerializerMethodField()
    unidade_administrativa = serializers.SerializerMethodField()
    is_superadmin = serializers.SerializerMethodField()
    permissoes = serializers.SerializerMethodField()
    tipo_usuario = serializers.SerializerMethodField()
    is_backoffice = serializers.SerializerMethodField()
    is_cidadao = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = (
            "id",
            "cpf",
            "nome",
            "email",
            "telefone",
            "endereco",
            "avatar",
            "perfil",
            "unidade_administrativa",
            "is_superadmin",
            "permissoes",
            "tipo_usuario",
            "is_backoffice",
            "is_cidadao",
        )

    def get_cpf(self, obj):
        return formatar_cpf(obj.cpf)

    def get_avatar(self, obj):
        return None

    def get_perfil(self, obj):
        pa = getattr(obj, "perfil_acesso", None)
        if not pa:
            return None
        return {
            "id": str(pa.id),
            "codigo": pa.codigo or "",
            "nome": pa.nome,
        }

    def get_unidade_administrativa(self, obj):
        unidade = getattr(obj, "unidade", None)
        if not unidade:
            return None
        return {
            "id": str(unidade.id),
            "nome": unidade.nome,
            "sigla": unidade.sigla or "",
        }

    def get_is_superadmin(self, obj):
        return usuario_e_super_admin(obj)

    def get_permissoes(self, obj):
        return listar_permissoes_efetivas(obj)

    def get_tipo_usuario(self, obj):
        return "backoffice" if usuario_e_backoffice(obj) else "cidadao"

    def get_is_backoffice(self, obj):
        return usuario_e_backoffice(obj)

    def get_is_cidadao(self, obj):
        return usuario_e_cidadao(obj)

    def get_endereco(self, obj):
        if not hasattr(obj, "endereco"):
            return None
        try:
            endereco = obj.endereco
        except EnderecoCidadao.DoesNotExist:
            return None
        data = {
            "cep": endereco.cep,
            "logradouro": endereco.logradouro,
            "numero": endereco.numero,
            "complemento": endereco.complemento,
            "bairro": endereco.bairro,
            "cidade": endereco.cidade,
            "estado": endereco.estado,
        }
        if endereco.localizacao:
            data["coordenadas"] = {
                "latitude": endereco.localizacao.y,
                "longitude": endereco.localizacao.x,
                "precisao": endereco.precisao,
            }
        return data


class RegisterSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=255)
    cpf = serializers.CharField(max_length=14)
    email = serializers.EmailField()
    telefone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    senha = serializers.CharField(write_only=True, min_length=8)
    endereco = EnderecoSerializer()

    def validate_cpf(self, value):
        if not cpf_valido(value):
            raise serializers.ValidationError(
                "Informe um CPF válido com os dígitos verificadores corretos."
            )
        cpf_norm = normalizar_cpf(value)
        if Usuario.objects.filter(cpf=cpf_norm).exists():
            raise serializers.ValidationError(
                "Este CPF já está cadastrado. Entre na sua conta ou recupere a senha."
            )
        return value

    def validate_email(self, value):
        if Usuario.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email já está em uso")
        return value

    def create(self, validated_data):
        endereco_data = validated_data.pop("endereco")
        coords = endereco_data.pop("coordenadas", None)
        cpf = normalizar_cpf(validated_data.pop("cpf"))
        senha = validated_data.pop("senha")

        user = Usuario.objects.create_user(
            cpf=cpf,
            senha=senha,
            metodo_autenticacao="padrao",
            **validated_data,
        )
        endereco = EnderecoCidadao.objects.create(
            usuario=user,
            precisao=coords.get("precisao", "cidade") if coords else "cidade",
            **endereco_data,
        )
        if coords:
            endereco.localizacao = Point(
                coords["longitude"], coords["latitude"], srid=4326
            )
            endereco.save(update_fields=["localizacao", "precisao"])
        return user


CAMPOS_AUTOEDITAVEIS_ME = frozenset({"nome", "email", "telefone", "endereco"})


class UsuarioPerfilUpdateSerializer(serializers.Serializer):
    """Atualização parcial de perfil do cidadão autenticado."""

    nome = serializers.CharField(max_length=255, required=False)
    email = serializers.EmailField(required=False)
    telefone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    endereco = EnderecoSerializer(required=False)

    def validate(self, attrs):
        request = self.context.get("request")
        if request is not None:
            proibidos = set(request.data.keys()) - CAMPOS_AUTOEDITAVEIS_ME
            if proibidos:
                raise serializers.ValidationError(
                    {
                        "detail": (
                            "Não é permitido alterar privilégios ou vínculos por esta rota. "
                            f"Campos rejeitados: {', '.join(sorted(proibidos))}."
                        )
                    }
                )
        if not attrs:
            raise serializers.ValidationError("Informe ao menos um campo para atualizar.")
        return attrs

    def validate_email(self, value):
        usuario = self.context["usuario"]
        if Usuario.objects.filter(email__iexact=value).exclude(pk=usuario.pk).exists():
            raise serializers.ValidationError("E-mail já está em uso")
        return value

    def save(self, **kwargs):
        usuario = self.context["usuario"]
        validated = dict(self.validated_data)
        endereco_data = validated.pop("endereco", None)

        campos_usuario = []
        for campo in ("nome", "email", "telefone"):
            if campo in validated:
                setattr(usuario, campo, validated[campo])
                campos_usuario.append(campo)
        if campos_usuario:
            usuario.save(update_fields=campos_usuario + ["updated_at"])

        if endereco_data is not None:
            coords = endereco_data.pop("coordenadas", None)
            endereco, _created = EnderecoCidadao.objects.get_or_create(
                usuario=usuario,
                defaults={
                    "precisao": coords.get("precisao", "cidade") if coords else "cidade",
                    **endereco_data,
                },
            )
            if not _created:
                for campo, valor in endereco_data.items():
                    setattr(endereco, campo, valor)
            if coords:
                endereco.localizacao = Point(
                    coords["longitude"], coords["latitude"], srid=4326
                )
                endereco.precisao = coords.get("precisao", endereco.precisao)
            endereco.save()

        return usuario


class AlterarSenhaSerializer(serializers.Serializer):
    senha_atual = serializers.CharField(write_only=True)
    nova_senha = serializers.CharField(write_only=True, min_length=8)
    confirmar_nova_senha = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        usuario = self.context["usuario"]
        if not usuario.check_password(attrs["senha_atual"]):
            raise serializers.ValidationError(
                {"senha_atual": "Senha atual incorreta."}
            )
        if attrs["nova_senha"] != attrs["confirmar_nova_senha"]:
            raise serializers.ValidationError(
                {"confirmar_nova_senha": "A confirmação não coincide com a nova senha."}
            )
        if attrs["senha_atual"] == attrs["nova_senha"]:
            raise serializers.ValidationError(
                {"nova_senha": "A nova senha deve ser diferente da atual."}
            )
        try:
            validate_password(attrs["nova_senha"], user=usuario)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"nova_senha": list(exc.messages)}) from exc
        return attrs

    def save(self, **kwargs):
        usuario = self.context["usuario"]
        usuario.set_password(self.validated_data["nova_senha"])
        usuario.save(update_fields=["password", "updated_at"])
        return usuario


class DesativarContaSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=False, allow_blank=True)


class LoginSerializer(serializers.Serializer):
    cpf = serializers.CharField()
    senha = serializers.CharField(write_only=True)

    def validate_cpf(self, value):
        if not cpf_valido(value):
            raise serializers.ValidationError("CPF inválido")
        return value


class VerificarCpfSerializer(serializers.Serializer):
    cpf = serializers.CharField(max_length=14)

    def validate_cpf(self, value):
        if not cpf_valido(value):
            raise serializers.ValidationError("CPF inválido")
        return normalizar_cpf(value)


class SolicitarRecuperacaoSenhaSerializer(serializers.Serializer):
    cpf = serializers.CharField(max_length=14)
    canal = serializers.ChoiceField(choices=["email", "sms", "whatsapp"])

    def validate_cpf(self, value):
        if not cpf_valido(value):
            raise serializers.ValidationError("CPF inválido")
        return normalizar_cpf(value)


class RedefinirSenhaRecuperacaoSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=128)
    nova_senha = serializers.CharField(write_only=True, min_length=8)


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class GovBrCallbackSerializer(serializers.Serializer):
    code = serializers.CharField()


class SsoMunicipalCallbackSerializer(serializers.Serializer):
    token = serializers.CharField()


class PushTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DispositivoPush
        fields = ("token", "plataforma")


class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = ("id", "titulo", "mensagem", "lida", "criado_em")
