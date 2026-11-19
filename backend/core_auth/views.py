"""Endpoints de autenticação e notificações."""

import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core_auth.jwt_utils import build_auth_response
from core_auth.models import DispositivoPush, Notificacao, RecuperacaoSenha, Usuario
from core_auth.serializers import (
    AlterarSenhaSerializer,
    DesativarContaSerializer,
    GovBrCallbackSerializer,
    LoginSerializer,
    NotificacaoSerializer,
    PushTokenSerializer,
    RedefinirSenhaRecuperacaoSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    SolicitarRecuperacaoSenhaSerializer,
    SsoMunicipalCallbackSerializer,
    UsuarioPerfilUpdateSerializer,
    UsuarioResponseSerializer,
    VerificarCpfSerializer,
)
from core_auth.lgpd_services import anonimizar_usuario
from core_auth.services.password_recovery import (
    enviar_recuperacao_senha,
    mascarar_email,
    mascarar_telefone,
)
from core_auth.utils import formatar_cpf, normalizar_cpf
from ouvia_core.pagination import ContractPagination

MENSAGEM_RECUPERACAO_GENERICA = (
    "Se o CPF estiver cadastrado, você receberá instruções para redefinir a senha "
    "pelo canal escolhido (e-mail, SMS ou WhatsApp)."
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(build_auth_response(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cpf = normalizar_cpf(serializer.validated_data["cpf"])
        senha = serializer.validated_data["senha"]
        user = authenticate(request, cpf=cpf, password=senha)
        if not user:
            return Response(
                {"error": {"code": "INVALID_CREDENTIALS", "message": "CPF ou senha inválidos"}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(build_auth_response(user))


class LogoutView(APIView):
    def post(self, request):
        return Response(status=status.HTTP_200_OK)


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh = RefreshToken(serializer.validated_data["refresh_token"])
            return Response({"token": str(refresh.access_token)})
        except TokenError:
            return Response(
                {"error": {"code": "INVALID_TOKEN", "message": "Refresh token inválido"}},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class GovBrAuthorizeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """Redireciona para o fluxo OAuth Gov.br (stub com URL configurável)."""
        return redirect(settings.GOVBR_AUTHORIZE_URL)


class GovBrCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GovBrCallbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, _ = Usuario.objects.get_or_create(
            cpf="12345678900",
            defaults={
                "nome": "João da Silva",
                "email": "joao.silva@email.com",
                "telefone": "(11) 98765-4321",
                "metodo_autenticacao": "govbr",
            },
        )
        user.metodo_autenticacao = "govbr"
        user.save(update_fields=["metodo_autenticacao"])
        return Response(build_auth_response(user))


class SsoMunicipalCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SsoMunicipalCallbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, _ = Usuario.objects.get_or_create(
            cpf="98765432100",
            defaults={
                "nome": "Maria Santos",
                "email": "maria.santos@prefeitura.gov.br",
                "telefone": "(11) 91234-5678",
                "metodo_autenticacao": "sso_municipal",
            },
        )
        return Response(build_auth_response(user))


class VerificarCpfView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerificarCpfSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cpf_norm = serializer.validated_data["cpf"]
        ja_cadastrado = Usuario.objects.filter(cpf=cpf_norm).exists()
        return Response(
            {
                "valido": True,
                "disponivel": not ja_cadastrado,
                "ja_cadastrado": ja_cadastrado,
                "mensagem": (
                    "Este CPF já está cadastrado. Entre na sua conta ou recupere a senha."
                    if ja_cadastrado
                    else "CPF válido e disponível para cadastro."
                ),
            }
        )


class SolicitarRecuperacaoSenhaView(APIView):
    """Solicita envio de link/código por e-mail, SMS ou WhatsApp (adapters configuráveis)."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SolicitarRecuperacaoSenhaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cpf = serializer.validated_data["cpf"]
        canal = serializer.validated_data["canal"]

        resposta_base = {
            "mensagem": MENSAGEM_RECUPERACAO_GENERICA,
            "canais_disponiveis": ["email", "sms", "whatsapp"],
        }

        usuario = Usuario.objects.filter(cpf=cpf).first()
        if not usuario:
            return Response({**resposta_base, "enviado": False})

        if canal == RecuperacaoSenha.Canal.EMAIL and not usuario.email:
            return Response(
                {
                    "error": {
                        "code": "CANAL_INDISPONIVEL",
                        "message": "Não há e-mail cadastrado para este CPF. Tente SMS ou WhatsApp.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if canal in (RecuperacaoSenha.Canal.SMS, RecuperacaoSenha.Canal.WHATSAPP) and not (
            usuario.telefone or ""
        ).strip():
            return Response(
                {
                    "error": {
                        "code": "CANAL_INDISPONIVEL",
                        "message": "Não há telefone cadastrado para este CPF. Tente o canal e-mail.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = secrets.token_urlsafe(48)
        expira_em = timezone.now() + timedelta(hours=settings.PASSWORD_RESET_TOKEN_TTL_HOURS)
        RecuperacaoSenha.objects.create(
            usuario=usuario,
            token=token,
            canal=canal,
            expira_em=expira_em,
        )

        base_url = settings.PASSWORD_RESET_FRONTEND_URL.rstrip("/")
        link = f"{base_url}?token={token}"
        enviar_recuperacao_senha(usuario, canal, token, link)

        destino = (
            mascarar_email(usuario.email)
            if canal == RecuperacaoSenha.Canal.EMAIL
            else mascarar_telefone(usuario.telefone)
        )

        return Response(
            {
                **resposta_base,
                "enviado": True,
                "canal": canal,
                "destino_mascarado": destino,
                "expira_em": expira_em.isoformat(),
            }
        )


class RedefinirSenhaRecuperacaoView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RedefinirSenhaRecuperacaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        nova_senha = serializer.validated_data["nova_senha"]

        recuperacao = (
            RecuperacaoSenha.objects.select_related("usuario").filter(token=token).first()
        )
        if (
            not recuperacao
            or recuperacao.utilizado_em
            or recuperacao.expira_em < timezone.now()
        ):
            return Response(
                {
                    "error": {
                        "code": "TOKEN_INVALIDO",
                        "message": "Link ou código de recuperação inválido ou expirado.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario = recuperacao.usuario
        usuario.set_password(nova_senha)
        usuario.save(update_fields=["password"])
        recuperacao.utilizado_em = timezone.now()
        recuperacao.save(update_fields=["utilizado_em"])

        return Response({"mensagem": "Senha redefinida com sucesso. Você já pode entrar."})


class NotificacaoListView(APIView):
    pagination_class = ContractPagination

    def get(self, request):
        qs = Notificacao.objects.filter(usuario=request.user)
        lidas = request.query_params.get("lidas")
        if lidas is not None:
            qs = qs.filter(lida=lidas.lower() == "true")
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request, view=self)
        serializer = NotificacaoSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class NotificacaoMarcarLidaView(APIView):
    def patch(self, request, pk):
        notif = Notificacao.objects.filter(usuario=request.user, pk=pk).first()
        if not notif:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "Notificação não encontrada"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        notif.lida = True
        notif.save(update_fields=["lida"])
        return Response(status=status.HTTP_200_OK)


class RegistrarPushView(APIView):
    def post(self, request):
        serializer = PushTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        DispositivoPush.objects.update_or_create(
            usuario=request.user,
            token=serializer.validated_data["token"],
            defaults={"plataforma": serializer.validated_data["plataforma"]},
        )
        return Response({"ok": True})


def _invalidar_tokens_usuario(usuario, refresh_raw: str = "") -> None:
    if refresh_raw:
        try:
            token = RefreshToken(refresh_raw)
            token.blacklist()
        except TokenError:
            pass

    try:
        from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

        for outstanding in OutstandingToken.objects.filter(user=usuario):
            BlacklistedToken.objects.get_or_create(token=outstanding)
    except Exception:
        logger = __import__("logging").getLogger(__name__)
        logger.info("Blacklist JWT indisponível; conta desativada via is_active.")


def _carregar_usuario_me(usuario):
    return (
        Usuario.objects.select_related("perfil_acesso", "unidade", "endereco")
        .filter(pk=usuario.pk)
        .first()
        or usuario
    )


class UsuarioMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = _carregar_usuario_me(request.user)
        return Response(UsuarioResponseSerializer(user).data)

    def patch(self, request):
        serializer = UsuarioPerfilUpdateSerializer(
            data=request.data,
            partial=True,
            context={"usuario": request.user, "request": request},
        )
        serializer.is_valid(raise_exception=True)
        usuario = _carregar_usuario_me(serializer.save())
        return Response(UsuarioResponseSerializer(usuario).data)


class AlterarSenhaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AlterarSenhaSerializer(
            data=request.data,
            context={"usuario": request.user},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"mensagem": "Senha alterada com sucesso."})


class AnonimizarUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        usuario = request.user
        refresh_raw = request.data.get("refresh_token", "")

        _invalidar_tokens_usuario(usuario, refresh_raw)
        anonimizar_usuario(usuario)

        return Response(
            {
                "mensagem": (
                    "Solicitação de anonimização registrada. "
                    "Seus dados pessoais serão removidos conforme a LGPD."
                ),
                "prazo_execucao": "48h",
            },
            status=status.HTTP_200_OK,
        )


class DesativarUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        serializer = DesativarContaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = request.user
        refresh_raw = serializer.validated_data.get("refresh_token") or ""

        _invalidar_tokens_usuario(usuario, refresh_raw)
        anonimizar_usuario(usuario)

        return Response(
            {
                "mensagem": "Conta desativada. Seus dados pessoais foram removidos do cadastro ativo."
            },
            status=status.HTTP_200_OK,
        )
