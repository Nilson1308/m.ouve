"""Exibição legível de valores de lookup (revisão / backoffice)."""

from django.test import TestCase

from atendimentos.campo_exibicao import formatar_valor_campo
from catalogo.datasources import LOOKUP_DATASOURCE_EQUIPAMENTOS


class FormatarValorLookupTests(TestCase):
    def test_nao_catalogado_exibe_somente_nome(self):
        prop = {
            "title": "Informe o equipamento público",
            "x-ouvia-datasource": LOOKUP_DATASOURCE_EQUIPAMENTOS,
        }
        valor = {
            "nao_catalogado": True,
            "texto": "UBS de Bras Cubas",
        }
        self.assertEqual(formatar_valor_campo(prop, valor), "UBS de Bras Cubas")

    def test_nao_catalogado_remove_prefixo_confirmacao_chat(self):
        prop = {
            "title": "Equipamento",
            "x-ouvia-datasource": LOOKUP_DATASOURCE_EQUIPAMENTOS,
        }
        valor = {
            "nao_catalogado": True,
            "texto": "✓ Informe o equipamento público: UBS de Bras Cubas",
        }
        self.assertEqual(formatar_valor_campo(prop, valor), "UBS de Bras Cubas")
        self.assertNotIn("{", formatar_valor_campo(prop, valor))
        self.assertNotIn("nao_catalogado", formatar_valor_campo(prop, valor))