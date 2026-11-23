"""Lookup público de equipamentos."""

from django.contrib.gis.geos import Point
from rest_framework import status
from rest_framework.test import APITestCase

from catalogo.models import EquipamentoPublico, UnidadeAdministrativa


class CatalogoLookupEquipamentosTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u_ativa = UnidadeAdministrativa.objects.create(
            nome="Secretaria de Saúde", sigla="SMS", ativo=True
        )
        cls.u_inativa = UnidadeAdministrativa.objects.create(
            nome="Secretaria Inativa", sigla="SIN", ativo=False
        )
        cls.ubs = EquipamentoPublico.objects.create(
            nome="UBS Vila São José",
            tipo=EquipamentoPublico.Tipo.UBS,
            unidade_responsavel=cls.u_ativa,
            apelidos=["Postinho Sao Jose"],
            bairro="Vila São José",
            ativo=True,
        )
        EquipamentoPublico.objects.create(
            nome="UBS Inativa",
            tipo=EquipamentoPublico.Tipo.UBS,
            unidade_responsavel=cls.u_ativa,
            ativo=False,
        )
        EquipamentoPublico.objects.create(
            nome="UBS Unidade Morta",
            tipo=EquipamentoPublico.Tipo.UBS,
            unidade_responsavel=cls.u_inativa,
            ativo=True,
        )
        EquipamentoPublico.objects.create(
            nome="Escola Municipal Alpha",
            tipo=EquipamentoPublico.Tipo.ESCOLA,
            unidade_responsavel=cls.u_ativa,
            ativo=True,
        )

    def test_lista_ativos_sem_auth(self):
        resp = self.client.get("/api/v1/catalogo/lookup/equipamentos")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data["datasource"], "equipamentos_publicos")
        nomes = {item["nome"] for item in data["items"]}
        self.assertIn("UBS Vila São José", nomes)
        self.assertNotIn("UBS Inativa", nomes)
        self.assertNotIn("UBS Unidade Morta", nomes)

    def test_busca_apelido_sem_acento(self):
        resp = self.client.get(
            "/api/v1/catalogo/lookup/equipamentos",
            {"busca": "sao jose"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.json()["items"]), 1)
        self.assertEqual(resp.json()["items"][0]["nome"], "UBS Vila São José")

    def test_filtro_tipo(self):
        resp = self.client.get(
            "/api/v1/catalogo/lookup/equipamentos",
            {"tipo": "escola"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        nomes = [i["nome"] for i in resp.json()["items"]]
        self.assertEqual(nomes, ["Escola Municipal Alpha"])

    def test_payload_campos(self):
        resp = self.client.get("/api/v1/catalogo/lookup/equipamentos", {"limit": 5})
        item = resp.json()["items"][0]
        self.assertEqual(
            set(item.keys()),
            {
                "id",
                "nome",
                "tipo",
                "bairro",
                "unidade_id",
                "unidade_nome",
                "latitude",
                "longitude",
            },
        )

    def test_lookup_rejeita_lat_sem_lng(self):
        resp = self.client.get(
            "/api/v1/catalogo/lookup/equipamentos",
            {"lat": "-23.55"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ordena_por_proximidade(self):
        perto = EquipamentoPublico.objects.create(
            nome="UBS Perto",
            tipo=EquipamentoPublico.Tipo.UBS,
            unidade_responsavel=self.u_ativa,
            localizacao=Point(-46.6334, -23.5506, srid=4326),
            ativo=True,
        )
        EquipamentoPublico.objects.create(
            nome="UBS Longe",
            tipo=EquipamentoPublico.Tipo.UBS,
            unidade_responsavel=self.u_ativa,
            localizacao=Point(-46.70, -23.60, srid=4326),
            ativo=True,
        )
        EquipamentoPublico.objects.create(
            nome="UBS Sem GPS",
            tipo=EquipamentoPublico.Tipo.UBS,
            unidade_responsavel=self.u_ativa,
            ativo=True,
        )
        resp = self.client.get(
            "/api/v1/catalogo/lookup/equipamentos",
            {
                "lat": "-23.5505",
                "lng": "-46.6333",
                "limit": 10,
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        items = resp.json()["items"]
        nomes = [i["nome"] for i in items]
        self.assertEqual(nomes[0], perto.nome)
        self.assertIn("distancia_metros", items[0])
        self.assertIsInstance(items[0]["distancia_metros"], int)
        self.assertIsNone(items[-1]["distancia_metros"])