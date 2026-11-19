"""Lookup público de unidades para campos do formulário."""

from rest_framework import status
from rest_framework.test import APITestCase

from catalogo.models import UnidadeAdministrativa


class CatalogoLookupUnidadesTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u_ativa = UnidadeAdministrativa.objects.create(
            nome="Secretaria Municipal de Saúde",
            sigla="SMS",
            ativo=True,
        )
        cls.u_inativa = UnidadeAdministrativa.objects.create(
            nome="Secretaria Inativa",
            sigla="SIN",
            ativo=False,
        )
        cls.u_educacao = UnidadeAdministrativa.objects.create(
            nome="Secretaria Municipal de Educação",
            sigla="SME",
            ativo=True,
        )

    def test_lista_unidades_ativas_sem_autenticacao(self):
        resp = self.client.get("/api/v1/catalogo/lookup/unidades")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data["datasource"], "unidades_administrativas")
        ids = {item["id"] for item in data["items"]}
        self.assertIn(str(self.u_ativa.id), ids)
        self.assertIn(str(self.u_educacao.id), ids)
        self.assertNotIn(str(self.u_inativa.id), ids)
        for item in data["items"]:
            self.assertEqual(set(item.keys()), {"id", "nome"})

    def test_filtro_busca_por_nome_ou_sigla(self):
        resp = self.client.get(
            "/api/v1/catalogo/lookup/unidades",
            {"busca": "Educa"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        nomes = [i["nome"] for i in resp.json()["items"]]
        self.assertEqual(nomes, ["Secretaria Municipal de Educação"])

    def test_rota_com_barra_final(self):
        resp = self.client.get("/api/v1/catalogo/lookup/unidades/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)