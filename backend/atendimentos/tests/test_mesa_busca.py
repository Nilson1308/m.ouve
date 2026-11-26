"""Regras de detecção de código vs. palavra livre na Mesa."""

from django.test import SimpleTestCase

from atendimentos.services.mesa_busca import parece_codigo_protocolo


class MesaBuscaCodigoTests(SimpleTestCase):
    def test_palavras_comuns_nao_sao_codigo(self):
        self.assertFalse(parece_codigo_protocolo("ilumin"))
        self.assertFalse(parece_codigo_protocolo("ilumina"))
        self.assertFalse(parece_codigo_protocolo("iluminação"))
        self.assertFalse(parece_codigo_protocolo("buraco"))

    def test_codigos_prot_e_multivalor(self):
        self.assertTrue(parece_codigo_protocolo("PROT-2026-004"))
        self.assertTrue(parece_codigo_protocolo("prot-99-001"))
        self.assertTrue(parece_codigo_protocolo("SUPER-2026-01"))