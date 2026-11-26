"""Sugestões iniciais contextuais do Copiloto — rotas e anti-vazamento de escopo."""

from django.test import SimpleTestCase

from atendimentos.services.agente_copiloto_sugestoes import (
    ROTAS_BACKOFFICE_VUE,
    obter_sugestoes_iniciais_copiloto,
)


class CopilotoSugestoesRotasTests(SimpleTestCase):
    def test_rotas_canonicas_alinhadas_ao_vue(self):
        self.assertIn("/backoffice/mesa-trabalho", ROTAS_BACKOFFICE_VUE)
        self.assertIn("/backoffice/dashboard", ROTAS_BACKOFFICE_VUE)
        self.assertIn("/backoffice/relatorios/sla-cobrancas", ROTAS_BACKOFFICE_VUE)

    def test_dashboard_eficiencia_alias_setorial_unidade(self):
        sugs = obter_sugestoes_iniciais_copiloto(
            "unidade",
            rota="/backoffice/dashboard/eficiencia",
        )
        self.assertEqual(len(sugs), 3)
        texto = " ".join(sugs).lower()
        self.assertIn("minha", texto)
        self.assertNotIn("secretarias", texto)

    def test_sla_cobrancas_unidade_sem_comparativo_secretarias(self):
        sugs = obter_sugestoes_iniciais_copiloto(
            "unidade",
            rota="/backoffice/relatorios/sla-cobrancas",
        )
        self.assertGreaterEqual(len(sugs), 2)
        for sug in sugs:
            low = sug.lower()
            self.assertNotIn("secretarias", low)
            self.assertNotIn("qual secretaria", low)
            self.assertNotIn("escalonamento para a controladoria", low)

    def test_controladoria_mesa_pode_ter_comparativo(self):
        sugs = obter_sugestoes_iniciais_copiloto(
            "controladoria",
            rota="/backoffice/mesa-trabalho",
        )
        self.assertEqual(len(sugs), 3)