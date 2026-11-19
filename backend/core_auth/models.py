"""Modelos de usuário, endereço e RBAC."""

import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.db import models

from core_auth.rbac import (
    perfil_exige_unidade,
    permissoes_padrao,
    sincronizar_flags_usuario,
)
from core_auth.utils import normalizar_cpf


class Papel(models.Model):
    """Papel RBAC (cidadão, gestor, operador, etc.)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.SlugField(unique=True, max_length=50)
    nome = models.CharField(max_length=120)
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = "papel"
        verbose_name_plural = "papéis"

    def __str__(self):
        return self.nome


class PerfilAcesso(models.Model):
    """Perfil RBAC dinâmico (padrão GLPI) — permissões granulares por módulo."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.SlugField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Identificador estável para integrações (ex.: super_admin).",
    )
    nome = models.CharField(max_length=120)
    descricao = models.TextField(blank=True)
    permissoes = models.JSONField(
        default=permissoes_padrao,
        help_text="Mapa módulo → ações booleanas (ver PERMISSOES_TEMPLATE).",
    )
    sistema = models.BooleanField(
        default=False,
        help_text="Perfis criados na migração/bootstrap; não devem ser excluídos.",
    )
    ativo = models.BooleanField(
        default=True,
        help_text="Perfis inativos não aparecem para vínculo em novos usuários.",
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "perfil de acesso"
        verbose_name_plural = "perfis de acesso"

    def __str__(self):
        return self.nome


class UsuarioManager(BaseUserManager):
    """Manager para autenticação por CPF."""

    def create_user(self, cpf, senha=None, **extra_fields):
        cpf_norm = normalizar_cpf(cpf)
        if not cpf_norm:
            raise ValueError("CPF é obrigatório")
        user = self.model(cpf=cpf_norm, **extra_fields)
        user.set_password(senha)
        user.save(using=self._db)
        return user

    def create_superuser(self, cpf, senha=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(cpf, senha, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Usuário cidadão / gestor do hub."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cpf = models.CharField(max_length=11, unique=True, db_index=True)
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    perfil_acesso = models.ForeignKey(
        PerfilAcesso,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="usuarios",
        help_text="Perfil RBAC dinâmico. Vazio para cidadãos.",
    )
    telefone = models.CharField(max_length=20, blank=True)
    metodo_autenticacao = models.CharField(
        max_length=30,
        default="padrao",
        choices=[
            ("padrao", "Cadastro padrão"),
            ("govbr", "Gov.br"),
            ("sso_municipal", "SSO Municipal"),
        ],
    )
    govbr_sub = models.CharField(max_length=255, blank=True)
    papeis = models.ManyToManyField(Papel, blank=True, related_name="usuarios")
    unidade = models.ForeignKey(
        "catalogo.UnidadeAdministrativa",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="servidores",
        help_text="Unidade administrativa do gestor setorial (painel de OS).",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UsuarioManager()

    USERNAME_FIELD = "cpf"
    REQUIRED_FIELDS = ["nome", "email"]

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"

    def __str__(self):
        return self.nome

    def get_full_name(self):
        return (self.nome or "").strip() or self.email

    def get_short_name(self):
        parte = (self.nome or "").strip().split()
        return parte[0] if parte else self.email

    @property
    def username(self):
        """Compatibilidade com helpers do Django/DRF que usam `username`."""
        return self.cpf

    def clean(self):
        super().clean()
        if not self.perfil_acesso_id:
            return
        pa = self.perfil_acesso
        if perfil_exige_unidade(pa) and not self.unidade_id:
            raise ValidationError(
                {"unidade": "Unidade administrativa é obrigatória para este perfil de acesso."}
            )
        if not perfil_exige_unidade(pa) and self.unidade_id:
            raise ValidationError(
                {"unidade": "Este perfil de acesso não aceita vínculo com unidade."}
            )

    def save(self, *args, **kwargs):
        if self.perfil_acesso_id:
            pa = self.perfil_acesso
            if perfil_exige_unidade(pa) and not self.unidade_id:
                raise ValidationError(
                    "Unidade administrativa é obrigatória para este perfil de acesso."
                )
            if not perfil_exige_unidade(pa):
                self.unidade_id = None
            sincronizar_flags_usuario(self)
        super().save(*args, **kwargs)

    def tem_permissao(self, modulo: str, acao: str) -> bool:
        from core_auth.rbac import usuario_tem_permissao

        return usuario_tem_permissao(self, modulo, acao)


class EnderecoCidadao(models.Model):
    """Endereço residencial com ponto PostGIS (longitude, latitude)."""

    class PrecisaoCoordenada(models.TextChoices):
        EXATA = "exata", "Exata"
        RUA = "rua", "Rua"
        CIDADE = "cidade", "Cidade"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name="endereco"
    )
    cep = models.CharField(max_length=9)
    logradouro = models.CharField(max_length=255)
    numero = models.CharField(max_length=20, blank=True)
    complemento = models.CharField(max_length=120, blank=True)
    bairro = models.CharField(max_length=120)
    cidade = models.CharField(max_length=120)
    estado = models.CharField(max_length=2)
    precisao = models.CharField(
        max_length=10,
        choices=PrecisaoCoordenada.choices,
        default=PrecisaoCoordenada.CIDADE,
    )
    localizacao = gis_models.PointField(geography=True, srid=4326, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "endereço do cidadão"
        verbose_name_plural = "endereços dos cidadãos"

    def set_coordenadas(self, latitude: float, longitude: float):
        """Armazena POINT(longitude, latitude) conforme PostGIS."""
        self.localizacao = gis_models.Point(longitude, latitude, srid=4326)


class DispositivoPush(models.Model):
    """Token FCM para notificações push."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="dispositivos_push"
    )
    token = models.CharField(max_length=512)
    plataforma = models.CharField(
        max_length=10,
        choices=[("web", "Web"), ("android", "Android"), ("ios", "iOS")],
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("usuario", "token")


class RecuperacaoSenha(models.Model):
    """Token de redefinição de senha com canal de envio (e-mail/SMS/WhatsApp)."""

    class Canal(models.TextChoices):
        EMAIL = "email", "E-mail"
        SMS = "sms", "SMS"
        WHATSAPP = "whatsapp", "WhatsApp"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="recuperacoes_senha"
    )
    token = models.CharField(max_length=128, unique=True, db_index=True)
    canal = models.CharField(max_length=12, choices=Canal.choices)
    expira_em = models.DateTimeField()
    utilizado_em = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "recuperação de senha"
        verbose_name_plural = "recuperações de senha"


class Notificacao(models.Model):
    """Notificação in-app do cidadão."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="notificacoes"
    )
    titulo = models.CharField(max_length=255)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
