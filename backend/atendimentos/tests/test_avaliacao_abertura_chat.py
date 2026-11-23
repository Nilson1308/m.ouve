"""Avaliação de satisfação com a abertura da solicitação no chat (pós-registro)."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from atendimentos.models import Protocolo, SessaoChat
from catalogo.models import CategoriaCatalogo, ServicoCatalogo

User = get_user_model()


class AvaliacaoAberturaChatTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cidadao = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Cidadão Abertura",
            email="abertura.chat@test.local",
        )
        cat = CategoriaCatalogo.objects.create(nome="Cat", slug="cat-abertura", ativo=True)
        servico = ServicoCatalogo.objects.create(categoria=cat, nome="Serv", ativo=True)
        cls.protocolo = Protocolo.objects.create(
            codigo="PROT-ABERT-1",
            usuario=cls.cidadao,
            servico=servico,
            descricao="Teste",
            status=Protocolo.Status.EM_ANDAMENTO,
        )
        cls.sessao = SessaoChat.objects.create(
            usuario=cls.cidadao,
            categoria_inicial="zeladoria",
            status=SessaoChat.Status.FINALIZADO_PROTOCOLO,
            protocolo_final=cls.protocolo,
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.cidadao)

    def test_avaliar_abertura_com_protocolo_em_andamento(self):
        url = f"/api/v1/chat/sessao/{self.sessao.id}/avaliar-abertura"
        resp = self.client.post(url, {"nota": 5, "comentario": "Foi fácil"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["nota"], 5)
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.nota_abertura, 5)

    def test_csat_protocolo_ainda_exige_resolvido(self):
        resp = self.client.post(
            "/api/v1/avaliacoes",
            {"protocolo_id": str(self.protocolo.id), "nota": 5},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)