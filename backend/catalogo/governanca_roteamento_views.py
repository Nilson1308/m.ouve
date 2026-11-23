"""CRUD governança — matriz de roteamento temático por serviço."""

from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from catalogo.governanca_roteamento_serializers import MatrizRoteamentoTematicoSerializer
from catalogo.models import MatrizRoteamentoTematico, ServicoCatalogo
from core_auth.permissions import PermissaoConfiguracoes


class _MatrizRoteamentoBase(APIView):
    permission_classes = [IsAuthenticated, PermissaoConfiguracoes]

    def _servico(self, servico_id):
        try:
            return ServicoCatalogo.objects.get(pk=servico_id, is_template=False)
        except ServicoCatalogo.DoesNotExist as exc:
            raise Http404("Serviço não encontrado.") from exc


class MatrizRoteamentoListCreateView(_MatrizRoteamentoBase):
    """GET lista / POST cria regra em ``/backoffice/catalogo/servicos/<id>/roteamento``."""

    def get(self, request, servico_id):
        servico = self._servico(servico_id)
        qs = (
            MatrizRoteamentoTematico.objects.filter(servico=servico)
            .select_related("unidade_sugerida")
            .order_by("chave_schema", "valor_condicao")
        )
        serializer = MatrizRoteamentoTematicoSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request, servico_id):
        servico = self._servico(servico_id)
        serializer = MatrizRoteamentoTematicoSerializer(
            data=request.data,
            context={"servico": servico, "request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MatrizRoteamentoDetailView(_MatrizRoteamentoBase):
    """PATCH / DELETE em ``.../roteamento/<regra_id>``."""

    def _regra(self, servico_id, regra_id):
        servico = self._servico(servico_id)
        try:
            return MatrizRoteamentoTematico.objects.select_related(
                "unidade_sugerida"
            ).get(pk=regra_id, servico=servico)
        except MatrizRoteamentoTematico.DoesNotExist:
            return None

    def patch(self, request, servico_id, regra_id):
        regra = self._regra(servico_id, regra_id)
        if not regra:
            return Response(
                {"detail": "Regra de roteamento não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = MatrizRoteamentoTematicoSerializer(
            regra,
            data=request.data,
            partial=True,
            context={"servico": regra.servico, "request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, servico_id, regra_id):
        regra = self._regra(servico_id, regra_id)
        if not regra:
            return Response(
                {"detail": "Regra de roteamento não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        regra.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)