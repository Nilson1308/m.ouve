"""Validação de campos lookup no Form Builder."""

from django.test import TestCase

from catalogo.form_builder import normalizar_formulario_schema
from catalogo.schema_mapper import formulario_schema_para_schema_formulario
from catalogo.schema_props import validar_schema_formulario_lookup


class FormBuilderLookupTests(TestCase):
    def test_normaliza_campo_lookup(self):
        lista = normalizar_formulario_schema(
            [
                {
                    "name": "unidade_referencia",
                    "type": "lookup",
                    "label": "Secretaria relacionada",
                    "datasource": "unidades_administrativas",
                    "required": False,
                }
            ]
        )
        self.assertEqual(lista[0]["type"], "lookup")
        self.assertEqual(lista[0]["datasource"], "unidades_administrativas")

    def test_schema_mapper_propaga_x_ouvia(self):
        schema = formulario_schema_para_schema_formulario(
            [
                {
                    "name": "unidade_ref",
                    "type": "lookup",
                    "label": "Unidade",
                    "datasource": "unidades_administrativas",
                    "ui_widget": "searchable_select",
                    "required": True,
                }
            ]
        )
        prop = schema["properties"]["unidade_ref"]
        self.assertEqual(prop["x-ouvia-datasource"], "unidades_administrativas")
        self.assertEqual(prop["x-ouvia-ui-widget"], "searchable_select")
        self.assertEqual(prop["format"], "uuid")
        validar_schema_formulario_lookup(schema)