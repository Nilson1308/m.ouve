"""CRUD governança — matriz de roteamento temático."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from catalogo.models import (
    CategoriaCatalogo,
    MatrizRoteamentoTematico,
    ServicoCatalogo,
    UnidadeAdministrativa,
)
from core_auth.models import PerfilAcesso
from core_auth.rbac import aplicar_regras_automaticas, permissoes_padrao

User = get_user_model()


def _perfil_configuracoes():
    base = permissoes_padrao()
    base["configuracoes"] = {
        "ler": True,
        "criar": True,
        "editar": True,
        "excluir": True,
    }
    return aplicar_regras_automaticas(base)


def _perfil_sem_configuracoes():
    base = permissoes_padrao()
    base["configuracoes"] = {
        "ler": False,
        "criar": False,
        "editar": False,
        "excluir": False,
    }
    return aplicar_regras_automaticas(base)


class MatrizRoteamentoGovernancaTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = CategoriaCatalogo.objects.create(
            nome="Cat Roteamento", slug="cat-roteamento", ativo=True
        )
        cls.unidade_saude = UnidadeAdministrativa.objects.create(
            nome="Secretaria de Saúde", sigla="SMS", ativo=True
        )
        cls.unidade_educacao = UnidadeAdministrativa.objects.create(
            nome="Secretaria de Educação", sigla="SME", ativo=True
        )
        cls.unidade_inativa = UnidadeAdministrativa.objects.create(
            nome="Inativa", sigla="INA", ativo=False
        )
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Serviço Roteamento",
            unidade_responsavel=cls.unidade_saude,
            ativo=True,
            fluxo_tramitacao=ServicoCatalogo.FluxoTramitacao.OUVIDORIA_ENCAMINHA,
        )
        cls.perfil_ok = PerfilAcesso.objects.create(
            codigo="teste_cfg_roteamento",
            nome="Config Roteamento",
            permissoes=_perfil_configuracoes(),
            ativo=True,
        )
        cls.perfil_negado = PerfilAcesso.objects.create(
            codigo="teste_sem_cfg",
            nome="Sem Config",
            permissoes=_perfil_sem_configuracoes(),
            ativo=True,
        )
        cls.admin = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Admin Catálogo",
            email="admin.roteamento@test.local",
            perfil_acesso=cls.perfil_ok,
        )
        cls.sem_perm = User.objects.create_user(
            cpf="15350946056",
            password="x",
            nome="Sem Perm",
            email="sem.roteamento@test.local",
            perfil_acesso=cls.perfil_negado,
        )

    def _url_lista(self):
        return f"/api/v1/backoffice/catalogo/servicos/{self.servico.id}/roteamento"

    def _url_detalhe(self, regra_id):
        return f"{self._url_lista()}/{regra_id}"

    def test_listagem_requer_permissao_configuracoes(self):
        self.client.force_authenticate(user=self.sem_perm)
        resp = self.client.get(self._url_lista())
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_crud_completo_e_duplicidade_400(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            "chave_schema": "categoria",
            "valor_condicao": "saude",
            "unidade_sugerida": str(self.unidade_saude.id),
            "ativo": True,
        }
        resp = self.client.post(self._url_lista(), payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["unidade_sugerida_nome"], "Secretaria de Saúde")
        regra_id = resp.data["id"]

        resp_dup = self.client.post(self._url_lista(), payload, format="json")
        self.assertEqual(resp_dup.status_code, status.HTTP_400_BAD_REQUEST)
        msg = resp_dup.data.get("detail") or (resp_dup.data.get("error") or {}).get(
            "message", ""
        )
        self.assertIn("chave_schema", msg)
        self.assertIn("valor_condicao", msg)

        resp_list = self.client.get(self._url_lista())
        self.assertEqual(resp_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp_list.data), 1)

        resp_patch = self.client.patch(
            self._url_detalhe(regra_id),
            {
                "valor_condicao": "saude_publica",
                "unidade_sugerida": str(self.unidade_educacao.id),
            },
            format="json",
        )
        self.assertEqual(resp_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_patch.data["valor_condicao"], "saude_publica")
        self.assertEqual(resp_patch.data["unidade_sugerida_nome"], "Secretaria de Educação")

        resp_del = self.client.delete(self._url_detalhe(regra_id))
        self.assertEqual(resp_del.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MatrizRoteamentoTematico.objects.filter(pk=regra_id).exists())

    def test_unidade_inativa_rejeitada(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(
            self._url_lista(),
            {
                "chave_schema": "setor",
                "valor_condicao": "x",
                "unidade_sugerida": str(self.unidade_inativa.id),
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)