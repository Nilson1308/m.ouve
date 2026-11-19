"""CRUD de textos padrão de despacho por unidade administrativa."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.models import TextoPadraoDespacho
from core_auth.permissions import PermissaoTextosPadrao
from atendimentos.textos_padrao_serializers import TextoPadraoDespachoSerializer


def queryset_textos_usuario(user):
    qs = TextoPadraoDespacho.objects.select_related("unidade")
    if getattr(user, "is_superuser", False):
        return qs.order_by("titulo")
    unidade_id = getattr(user, "unidade_id", None)
    if not unidade_id:
        return qs.none()
    return qs.filter(unidade_id=unidade_id).order_by("titulo")


def unidade_efetiva_usuario(user):
    if getattr(user, "is_superuser", False):
        return None
    return getattr(user, "unidade_id", None)


class TextoPadraoListCreateView(APIView):
    permission_classes = [IsAuthenticated, PermissaoTextosPadrao]

    def get(self, request):
        qs = queryset_textos_usuario(request.user)
        data = TextoPadraoDespachoSerializer(qs, many=True).data
        return Response({"results": data, "count": len(data)})

    def post(self, request):
        unidade_id = unidade_efetiva_usuario(request.user)
        if not unidade_id and not request.user.is_superuser:
            return Response(
                {"detail": "Usuário sem unidade administrativa vinculada."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if request.user.is_superuser:
            unidade_id = request.data.get("unidade") or unidade_id
            if not unidade_id:
                return Response(
                    {"detail": "Informe unidade para criar o texto padrão."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        payload = {**request.data, "unidade": unidade_id}
        serializer = TextoPadraoDespachoSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(unidade_id=unidade_id)
        return Response(
            TextoPadraoDespachoSerializer(obj).data,
            status=status.HTTP_201_CREATED,
        )


class TextoPadraoDetailView(APIView):
    permission_classes = [IsAuthenticated, PermissaoTextosPadrao]

    def get_object(self, request, pk):
        qs = queryset_textos_usuario(request.user)
        return get_object_or_404(qs, pk=pk)

    def get(self, request, pk):
        obj = self.get_object(request, pk)
        return Response(TextoPadraoDespachoSerializer(obj).data)

    def put(self, request, pk):
        obj = self.get_object(request, pk)
        serializer = TextoPadraoDespachoSerializer(
            obj, data=request.data, partial=False
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TextoPadraoDespachoSerializer(obj).data)

    def delete(self, request, pk):
        obj = self.get_object(request, pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
