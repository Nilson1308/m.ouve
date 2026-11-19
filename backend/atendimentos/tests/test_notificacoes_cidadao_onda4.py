"""Onda 4 — Notificações cidadão (in-app) e Web Push."""

from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from atendimentos.models import NotificacaoCidadao, Protocolo, PushSubscription
from atendimentos.notificacoes_cidadao import criar_notificacao_cidadao, notificar_status_protocolo
from catalogo.models import CategoriaCatalogo, ServicoCatalogo, UnidadeAdministrativa

User = get_user_model()


class NotificacoesCidadaoApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cidadao = User.objects.create_user(
            cpf="52998224725",
            password="x",
            nome="Cidadão Notif",
            email="cid.notif@test.local",
        )
        cls.outro = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Outro",
            email="outro@test.local",
        )
        unidade = UnidadeAdministrativa.objects.create(nome="UA", sigla="UA", ativo=True)
        cat = CategoriaCatalogo.objects.create(nome="Cat", slug="cat-notif", ativo=True)
        servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Serv",
            unidade_responsavel=unidade,
            ativo=True,
        )
        cls.protocolo = Protocolo.objects.create(
            codigo="PROT-NOTIF-1",
            usuario=cls.cidadao,
            servico=servico,
            descricao="Teste notificação",
            status=Protocolo.Status.EM_ANDAMENTO,
        )
        cls.notif = NotificacaoCidadao.objects.create(
            usuario=cls.cidadao,
            protocolo=cls.protocolo,
            titulo="Teste",
            mensagem="Corpo da notificação",
            lida=False,
        )
        NotificacaoCidadao.objects.create(
            usuario=cls.cidadao,
            titulo="Lida",
            mensagem="Já lida",
            lida=True,
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.cidadao)

    def test_lista_notificacoes_e_contador_nao_lidas(self):
        resp = self.client.get("/api/v1/app/notificacoes")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["nao_lidas"], 1)
        self.assertEqual(resp["X-Notificacoes-Nao-Lidas"], "1")
        self.assertGreaterEqual(len(resp.data["results"]), 1)
        primeiro = resp.data["results"][0]
        self.assertIn("protocolo_codigo", primeiro)

    def test_marcar_lida_apenas_propria(self):
        url = f"/api/v1/app/notificacoes/{self.notif.id}/marcar-lida"
        resp = self.client.patch(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.notif.refresh_from_db()
        self.assertTrue(self.notif.lida)

        self.client.force_authenticate(user=self.outro)
        resp2 = self.client.patch(url)
        self.assertEqual(resp2.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(VAPID_PUBLIC_KEY="BChavePublicaTeste123")
    def test_vapid_public_key_endpoint(self):
        resp = self.client.get("/api/v1/app/notificacoes/vapid-public-key")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["configurado"])
        self.assertEqual(resp.data["vapid_public_key"], "BChavePublicaTeste123")

        self.client.force_authenticate(user=None)
        resp_anon = self.client.get("/api/v1/app/notificacoes/vapid-public-key")
        self.assertEqual(resp_anon.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(VAPID_PUBLIC_KEY="")
    def test_vapid_public_key_sem_config(self):
        resp = self.client.get("/api/v1/app/notificacoes/vapid-public-key")
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertFalse(resp.data["configurado"])

    def test_push_subscribe_cria_e_atualiza(self):
        payload = {
            "endpoint": "https://push.example.test/sub/abc",
            "keys": {
                "p256dh": "BKx" * 20,
                "auth": "auth-secret-123",
            },
        }
        resp = self.client.post("/api/v1/app/notificacoes/push-subscribe", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PushSubscription.objects.filter(usuario=self.cidadao).count(), 1)

        payload["keys"]["auth"] = "auth-novo"
        resp2 = self.client.post("/api/v1/app/notificacoes/push-subscribe", payload, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)
        sub = PushSubscription.objects.get(endpoint=payload["endpoint"])
        self.assertEqual(sub.auth, "auth-novo")
        self.assertEqual(sub.usuario_id, self.cidadao.pk)


class NotificacoesCidadaoTaskTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cidadao = User.objects.create_user(
            cpf="15350946056",
            password="x",
            nome="Cidadão Task",
            email="task@test.local",
        )
        unidade = UnidadeAdministrativa.objects.create(nome="UB", sigla="UB", ativo=True)
        cat = CategoriaCatalogo.objects.create(nome="Cat2", slug="cat-task", ativo=True)
        servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Serv2",
            unidade_responsavel=unidade,
            ativo=True,
        )
        cls.protocolo = Protocolo.objects.create(
            codigo="PROT-TASK",
            usuario=cls.cidadao,
            servico=servico,
            descricao="Task",
            status=Protocolo.Status.RESOLVIDO,
        )

    @patch("atendimentos.tasks.enviar_notificacao_push_task.delay")
    def test_criar_notificacao_enfileira_task(self, delay_mock):
        with self.captureOnCommitCallbacks(execute=True):
            notif = criar_notificacao_cidadao(
                usuario=self.cidadao,
                titulo="Fila",
                mensagem="Teste fila Celery",
                protocolo=self.protocolo,
            )
        delay_mock.assert_called_once_with(str(notif.id))

    def test_gatilho_status_resolvido(self):
        with patch("atendimentos.tasks.enviar_notificacao_push_task.delay") as delay_mock:
            with self.captureOnCommitCallbacks(execute=True):
                notif = notificar_status_protocolo(self.protocolo)
            self.assertIsNotNone(notif)
            delay_mock.assert_called_once()

    @override_settings(
        VAPID_PUBLIC_KEY="test-pub",
        VAPID_PRIVATE_KEY="test-priv",
        VAPID_ADMIN_EMAIL="mailto:test@ouve.local",
    )
    @patch("pywebpush.webpush")
    def test_enviar_push_chama_pywebpush(self, webpush_mock):
        notif = NotificacaoCidadao.objects.create(
            usuario=self.cidadao,
            protocolo=self.protocolo,
            titulo="Push",
            mensagem="Corpo push",
        )
        PushSubscription.objects.create(
            usuario=self.cidadao,
            endpoint="https://push.example.test/sub/xyz",
            p256dh="k" * 40,
            auth="a" * 16,
        )
        from atendimentos.notificacoes_push import enviar_push_para_notificacao

        stats = enviar_push_para_notificacao(str(notif.id))
        self.assertEqual(stats["enviados"], 1)
        webpush_mock.assert_called_once()