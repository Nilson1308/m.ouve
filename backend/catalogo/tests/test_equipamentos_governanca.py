"""CRUD backoffice — equipamentos públicos."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from catalogo.models import EquipamentoPublico, UnidadeAdministrativa
from core_auth.models import PerfilAcesso
from core_auth.rbac import aplicar_regras_automaticas, permissoes_padrao

User = get_user_model()


def _perfil_configuracoes():
    base = permissoes_padrao()
    base["configuracoes"] = {"ler": True, "criar": True, "editar": True, "excluir": True}
    return aplicar_regras_automaticas(base)


def _perfil_sem_configuracoes():
    base = permissoes_padrao()
    base["configuracoes"] = {"ler": False, "criar": False, "editar": False, "excluir": False}
    return aplicar_regras_automaticas(base)


class EquipamentosGovernancaTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u_saude = UnidadeAdministrativa.objects.create(
            nome="Secretaria de Saúde", sigla="SMS", ativo=True
        )
        cls.u_inativa = UnidadeAdministrativa.objects.create(
            nome="Unidade Inativa", sigla="IN", ativo=False
        )
        cls.perfil_ok = PerfilAcesso.objects.create(
            codigo="teste_cfg_equip",
            nome="Config Equip",
            permissoes=_perfil_configuracoes(),
            ativo=True,
        )
        cls.perfil_negado = PerfilAcesso.objects.create(
            codigo="teste_sem_cfg_equip",
            nome="Sem Config",
            permissoes=_perfil_sem_configuracoes(),
            ativo=True,
        )
        cls.admin = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Admin",
            email="admin.equip@test.local",
            perfil_acesso=cls.perfil_ok,
            is_staff=True,
        )
        cls.sem_perm = User.objects.create_user(
            cpf="15350946056",
            password="x",
            nome="Sem perm",
            email="sem.equip@test.local",
            perfil_acesso=cls.perfil_negado,
            is_staff=True,
        )
        cls.ubs = EquipamentoPublico.objects.create(
            nome="UBS Central",
            tipo=EquipamentoPublico.Tipo.UBS,
            unidade_responsavel=cls.u_saude,
            apelidos=["Postinho do Centro"],
            bairro="Centro",
            ativo=True,
        )

    def test_listagem_requer_configuracoes(self):
        self.client.force_authenticate(user=self.sem_perm)
        resp = self.client.get("/api/v1/backoffice/equipamentos")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_cria_equipamento_com_unidade_ativa(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            "nome": "Escola Municipal João",
            "tipo": "escola",
            "unidade_responsavel": str(self.u_saude.id),
            "apelidos": ["  EM João ", "EM Joao"],
            "bairro": "Vila Nova",
            "ativo": True,
        }
        resp = self.client.post("/api/v1/backoffice/equipamentos", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.json()
        self.assertEqual(data["unidade_responsavel_nome"], "Secretaria de Saúde")
        self.assertEqual(data["apelidos"], ["EM João", "EM Joao"])

    def test_rejeita_unidade_inativa(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            "nome": "CRAS Teste",
            "tipo": "cras",
            "unidade_responsavel": str(self.u_inativa.id),
            "apelidos": [],
        }
        resp = self.client.post("/api/v1/backoffice/equipamentos", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filtro_busca_apelido(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(
            "/api/v1/backoffice/equipamentos",
            {"busca": "Postinho"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        nomes = [item["nome"] for item in resp.json()]
        self.assertIn("UBS Central", nomes)