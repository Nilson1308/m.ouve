"""Onda 2 — perfil /me, alterar senha e enforcement RBAC granular."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core_auth.models import PerfilAcesso
from core_auth.rbac import aplicar_regras_automaticas, permissoes_padrao

User = get_user_model()


def _perfil_apenas_mesa_ler():
    base = permissoes_padrao()
    base["mesa_trabalho"] = {"ler": True, "criar": False, "editar": False, "excluir": False}
    return aplicar_regras_automaticas(base)


def _perfil_sem_mesa():
    return aplicar_regras_automaticas(permissoes_padrao())


class MePerfilSenhaRBACTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.perfil_leitura = PerfilAcesso.objects.create(
            codigo="teste_mesa_ler",
            nome="Teste Mesa Ler",
            permissoes=_perfil_apenas_mesa_ler(),
            ativo=True,
        )
        self.perfil_vazio = PerfilAcesso.objects.create(
            codigo="teste_sem_perms",
            nome="Sem permissões",
            permissoes=_perfil_sem_mesa(),
            ativo=True,
        )
        self.usuario = User.objects.create_user(
            cpf="39053344705",
            password="SenhaAntiga1!",
            nome="Servidor Teste",
            email="servidor.onda2@test.local",
            perfil_acesso=self.perfil_leitura,
        )
        self.usuario_sem_mesa = User.objects.create_user(
            cpf="15350946056",
            password="SenhaAntiga1!",
            nome="Sem Mesa",
            email="semmesa.onda2@test.local",
            perfil_acesso=self.perfil_vazio,
        )

    def _auth(self, user=None):
        user = user or self.usuario
        self.client.force_authenticate(user=user)

    def test_get_me_inclui_permissoes_e_tipo_conta(self):
        self._auth()
        response = self.client.get("/api/v1/auth/me")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIn("mesa_trabalho.ler", data["permissoes"])
        self.assertTrue(data["is_backoffice"])
        self.assertEqual(data["tipo_usuario"], "backoffice")
        self.assertEqual(data["perfil"]["codigo"], "teste_mesa_ler")
        self.assertFalse(data["is_superadmin"])

    def test_patch_me_atualiza_telefone(self):
        self._auth()
        response = self.client.patch(
            "/api/v1/usuario/me",
            {"telefone": "(11) 99999-0000"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.telefone, "(11) 99999-0000")

    def test_patch_me_bloqueia_escalacao_privilegio(self):
        self._auth()
        response = self.client.patch(
            "/api/v1/usuario/me",
            {"is_staff": True, "perfil_acesso": str(self.perfil_vazio.id)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.perfil_acesso_id, self.perfil_leitura.id)

    def test_alterar_senha_sucesso(self):
        self.usuario.set_password("SenhaAntiga1!")
        self.usuario.save(update_fields=["password"])
        self._auth()
        response = self.client.post(
            "/api/v1/auth/me/alterar-senha",
            {
                "senha_atual": "SenhaAntiga1!",
                "nova_senha": "Xk9$mPz2wQn8vL4rT6yU!",
                "confirmar_nova_senha": "Xk9$mPz2wQn8vL4rT6yU!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.check_password("Xk9$mPz2wQn8vL4rT6yU!"))

    def test_alterar_senha_senha_atual_incorreta(self):
        self._auth()
        response = self.client.post(
            "/api/v1/usuario/alterar-senha",
            {
                "senha_atual": "errada",
                "nova_senha": "Xk9$mPz2wQn8vL4rT6yU!",
                "confirmar_nova_senha": "Xk9$mPz2wQn8vL4rT6yU!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        details = response.data.get("error", {}).get("details") or response.data
        self.assertIn("senha_atual", details)

    def test_backoffice_kanban_403_sem_permissao_mesa(self):
        self._auth(self.usuario_sem_mesa)
        response = self.client.get("/api/v1/backoffice/kanban")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_backoffice_kanban_200_com_mesa_ler(self):
        self._auth(self.usuario)
        response = self.client.get("/api/v1/backoffice/kanban")
        self.assertEqual(response.status_code, status.HTTP_200_OK)