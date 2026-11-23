from django.test import TestCase

from catalogo.formulario_resolution import formulario_schema_para_edicao
from catalogo.schema_mapper import (
    formulario_schema_para_schema_formulario,
    schema_formulario_para_formulario_schema,
)


class FormularioResolutionTests(TestCase):
    def test_ida_e_volta_schema(self):
        origem = [
            {
                "name": "tipo_problema",
                "type": "select",
                "label": "Tipo",
                "required": True,
                "options": [{"value": "buraco", "label": "Buraco"}],
                "ia_instrucao": "Identifique o defeito",
            },
            {
                "name": "localizacao",
                "type": "geo",
                "label": "Local",
                "required": True,
            },
        ]
        schema = formulario_schema_para_schema_formulario(origem)
        reconstruido = schema_formulario_para_formulario_schema(schema)
        self.assertEqual(len(reconstruido), 2)
        self.assertEqual(reconstruido[0]["name"], "tipo_problema")
        self.assertEqual(reconstruido[0]["type"], "select")

    def test_importa_quando_formulario_vazio(self):
        schema = formulario_schema_para_schema_formulario(
            [{"name": "descricao", "type": "textarea", "label": "Relato", "required": True}]
        )
        lista, importado = formulario_schema_para_edicao(formulario=[], schema_formulario=schema)
        self.assertTrue(importado)
        self.assertEqual(lista[0]["name"], "descricao")
        self.assertEqual(lista[0]["type"], "textarea")


class ReidratarServiceTests(TestCase):
    def test_seed_limpeza_tem_campos(self):
        from catalogo.reidratar_service import resolver_origem_reidratar
        from catalogo.models import ServicoCatalogo
        from unittest.mock import Mock

        servico = Mock(spec=ServicoCatalogo)
        servico.nome = "Limpeza Urbana"
        form, schema = resolver_origem_reidratar(servico)
        self.assertGreater(len(form), 0)
        self.assertTrue(schema.get("properties"))