"""Backoffice — modo de abertura do PWA."""

from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.models import ConfiguracaoSistema
from atendimentos.pwa_abertura import MODO_ABERTURA_PWA_CHOICES
from catalogo.pwa_catalogo import invalidar_cache_config_pwa
from core_auth.permissions import PermissaoConfiguracoes

_MODO_VALIDOS = {c[0] for c in MODO_ABERTURA_PWA_CHOICES}


class ConfiguracaoAtendimentoPwaSerializer(serializers.Serializer):
    modo_abertura_pwa = serializers.ChoiceField(choices=MODO_ABERTURA_PWA_CHOICES)


class ConfiguracaoAtendimentoPwaView(APIView):
    permission_classes = [IsAuthenticated, PermissaoConfiguracoes]

    def get(self, request):
        cfg = ConfiguracaoSistema.load()
        return Response({"modo_abertura_pwa": cfg.modo_abertura_pwa})

    def patch(self, request):
        cfg = ConfiguracaoSistema.load()
        ser = ConfiguracaoAtendimentoPwaSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        modo = ser.validated_data.get("modo_abertura_pwa")
        if modo is not None:
            if modo not in _MODO_VALIDOS:
                raise serializers.ValidationError({"modo_abertura_pwa": "Valor inválido."})
            cfg.modo_abertura_pwa = modo
            cfg.save(update_fields=["modo_abertura_pwa", "atualizado_em"])
            invalidar_cache_config_pwa()
        return Response({"modo_abertura_pwa": cfg.modo_abertura_pwa}, status=status.HTTP_200_OK)