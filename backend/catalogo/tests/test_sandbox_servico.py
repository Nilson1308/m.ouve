"""Sandbox do catálogo — não deve 500 com SessaoSandbox."""

from django.test import TestCase

from catalogo.models import CategoriaCatalogo, ServicoCatalogo, UnidadeAdministrativa
from catalogo.sandbox_service import executar_sandbox_servico_catalogo


class SandboxServicoCatalogoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.unidade = UnidadeAdministrativa.objects.create(
            nome="Teste", sigla="TST", ativo=True
        )
        cat = CategoriaCatalogo.objects.create(nome="Cat", slug="cat-sb", ativo=True)
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Serviço teste sandbox",
            unidade_responsavel=cls.unidade,
            ativo=True,
            schema_formulario={
                "type": "object",
                "properties": {
                    "relato": {"type": "string", "title": "Relato"},
                },
                "required": ["relato"],
            },
            formulario_schema=[{"name": "relato", "label": "Relato", "type": "text"}],
        )

    def test_primeiro_turno_vazio_retorna_200_em_memoria(self):
        out = executar_sandbox_servico_catalogo(self.servico, mensagem="")
        self.assertEqual(out.get("modo"), "sandbox")
        self.assertIn("resposta_cidadao", out)
        self.assertNotIn("erro", out)