from unittest.mock import patch

from django.test import TestCase, override_settings

from atendimentos.models import MensagemChat, SessaoChat
from atendimentos.slot_filling_service import (
    aplicar_slot_filling_abertura,
    montar_prefixo_confirmacao,
    texto_elegivel_abertura,
    validar_campos_extraidos,
)
from catalogo.models import CategoriaCatalogo, ServicoCatalogo
from django.contrib.auth import get_user_model


def _schema_ouvidoria():
    return {
        "type": "object",
        "properties": {
            "o": {
                "type": "string",
                "title": "Tipo",
                "enum": ["reclamacao", "elogio", "sugestao"],
                "enumNames": ["Reclamação", "Elogio", "Sugestão"],
            },
            "q": {
                "type": "string",
                "title": "Área",
                "enum": ["saude", "educacao", "zeladoria"],
                "enumNames": ["Saúde", "Educação", "Zeladoria"],
            },
            "d": {
                "type": "string",
                "title": "Descrição",
                "minLength": 25,
            },
        },
        "required": ["o", "q", "d"],
        "$metadata": {"ordem_campos": ["o", "q", "d"]},
    }


class TextoElegivelTests(TestCase):
    def test_rejeita_curto(self):
        self.assertFalse(texto_elegivel_abertura("oi"))
        self.assertFalse(texto_elegivel_abertura("sim"))

    def test_aceita_relato(self):
        t = "Quero reclamar que faltou médico na UBS do centro"
        self.assertTrue(texto_elegivel_abertura(t))


class ValidarCamposExtraidosTests(TestCase):
    def setUp(self):
        self.schema = _schema_ouvidoria()
        self.props = self.schema["properties"]

    def test_enum_valido(self):
        raw = {
            "o": {"valor": "Reclamação", "confianca": 0.95},
        }
        from catalogo.models import ServicoCatalogo

        servico = ServicoCatalogo(schema_formulario=self.schema)
        aceitos = validar_campos_extraidos(servico, raw, {})
        self.assertEqual(aceitos.get("o"), "reclamacao")

    def test_enum_invalido_descartado(self):
        raw = {"o": {"valor": "futebol", "confianca": 0.99}}
        servico = ServicoCatalogo(schema_formulario=self.schema)
        aceitos = validar_campos_extraidos(servico, raw, {})
        self.assertNotIn("o", aceitos)

    def test_confianca_baixa_descartada(self):
        raw = {"q": {"valor": "saude", "confianca": 0.5}}
        servico = ServicoCatalogo(schema_formulario=self.schema)
        aceitos = validar_campos_extraidos(servico, raw, {})
        self.assertEqual(aceitos, {})

    def test_descricao_rica_ok(self):
        texto = (
            "Na UBS do centro não tinha médico na segunda-feira e passei horas esperando atendimento."
        )
        raw = {"d": {"valor": texto, "confianca": 0.9}}
        servico = ServicoCatalogo(schema_formulario=self.schema)
        aceitos = validar_campos_extraidos(servico, raw, {})
        self.assertEqual(aceitos.get("d"), texto)

    def test_intencao_vaga_descricao_vazia(self):
        raw = {"d": {"valor": "quero fazer uma reclamação na saúde", "confianca": 0.9}}
        servico = ServicoCatalogo(schema_formulario=self.schema)
        aceitos = validar_campos_extraidos(servico, raw, {})
        self.assertNotIn("d", aceitos)

    def test_nao_sobrescreve_existente(self):
        raw = {"o": {"valor": "elogio", "confianca": 0.95}}
        servico = ServicoCatalogo(schema_formulario=self.schema)
        aceitos = validar_campos_extraidos(servico, raw, {"o": "reclamacao"})
        self.assertEqual(aceitos, {})


class AplicarSlotFillingIntegrationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            cpf="52998224725",
            password="x",
            nome="Slot Test",
            email="slot@test.local",
        )
        cat = CategoriaCatalogo.objects.create(
            nome="Ouvidoria",
            slug="ouvidoria-test-slot",
            tipo_legado="ouvidoria",
        )
        self.servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Ouvidoria Test",
            schema_formulario=_schema_ouvidoria(),
            ativo=True,
        )
        self.sessao = SessaoChat.objects.create(
            usuario=self.user,
            categoria_inicial="Ouvidoria",
            servico_identificado=self.servico,
        )
        self.texto_rico = (
            "Quero registrar uma reclamação na área da saúde: faltou médico na UBS do centro ontem."
        )

    @patch("atendimentos.slot_filling_service._chamar_llm_slot_filling")
    def test_frase_rica_preenche_varios(self, mock_llm):
        mock_llm.return_value = {
            "campos": {
                "o": {"valor": "reclamacao", "confianca": 0.92},
                "q": {"valor": "saude", "confianca": 0.88},
                "d": {"valor": self.texto_rico, "confianca": 0.9},
            }
        }
        MensagemChat.objects.create(
            sessao=self.sessao,
            autor="cidadao",
            conteudo_texto=self.texto_rico,
        )
        prefixo, aplicados = aplicar_slot_filling_abertura(self.sessao, self.servico)
        self.assertEqual(len(aplicados), 3)
        self.assertIn("Entendi!", prefixo)
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.dados_coletados.get("o"), "reclamacao")

    @patch("atendimentos.slot_filling_service._chamar_llm_slot_filling")
    def test_parcial_so_tipo_e_area(self, mock_llm):
        mock_llm.return_value = {
            "campos": {
                "o": {"valor": "reclamacao", "confianca": 0.9},
                "q": {"valor": "saude", "confianca": 0.85},
            }
        }
        MensagemChat.objects.create(
            sessao=self.sessao,
            autor="cidadao",
            conteudo_texto="Quero reclamar sobre a saúde pública municipal",
        )
        _prefixo, aplicados = aplicar_slot_filling_abertura(self.sessao, self.servico)
        self.assertIn("o", aplicados)
        self.assertIn("q", aplicados)
        self.assertNotIn("d", aplicados)

    @patch("atendimentos.slot_filling_service._chamar_llm_slot_filling")
    def test_fora_escopo_preenche_descricao(self, mock_llm):
        futebol = "Quero reclamar do meu time de futebol que está perdendo muito"
        mock_llm.return_value = {
            "campos": {
                "d": {"valor": futebol, "confianca": 0.91},
            }
        }
        MensagemChat.objects.create(
            sessao=self.sessao,
            autor="cidadao",
            conteudo_texto=futebol,
        )
        _, aplicados = aplicar_slot_filling_abertura(self.sessao, self.servico)
        self.assertIn("d", aplicados)

    @patch("atendimentos.slot_filling_service._chamar_llm_slot_filling")
    @override_settings(LLM_CHAT_API_KEY="")
    def test_fallback_sem_api_key(self, mock_llm):
        MensagemChat.objects.create(
            sessao=self.sessao,
            autor="cidadao",
            conteudo_texto=self.texto_rico,
        )
        prefixo, aplicados = aplicar_slot_filling_abertura(self.sessao, self.servico)
        self.assertEqual(aplicados, {})
        mock_llm.assert_not_called()

    @patch("atendimentos.llm_orchestrator._avaliar_regras_elegibilidade_detalhe")
    @patch("atendimentos.slot_filling_service._chamar_llm_slot_filling")
    def test_bloqueio_elegibilidade_apos_slot(self, mock_llm, mock_regras):
        futebol = "Quero reclamar do meu time de futebol que está perdendo muito"
        mock_llm.return_value = {"campos": {"d": {"valor": futebol, "confianca": 0.92}}}
        mock_regras.return_value = ("Fora de escopo municipal.", "Protocolo · teste")
        MensagemChat.objects.create(
            sessao=self.sessao,
            autor="cidadao",
            conteudo_texto=futebol,
        )
        aplicar_slot_filling_abertura(self.sessao, self.servico)
        from atendimentos.llm_orchestrator import LLMOrchestrator

        det = LLMOrchestrator().passo_deterministico_preenchimento(self.sessao)
        self.assertTrue(det.fluxo_bloqueado)
        self.assertIn("Fora de escopo", det.resposta_cidadao)

    @patch("atendimentos.slot_filling_service._chamar_llm_slot_filling", return_value=None)
    def test_fallback_llm_none(self, mock_llm):
        MensagemChat.objects.create(
            sessao=self.sessao,
            autor="cidadao",
            conteudo_texto=self.texto_rico,
        )
        prefixo, aplicados = aplicar_slot_filling_abertura(self.sessao, self.servico)
        self.assertEqual(aplicados, {})


class PrefixoTests(TestCase):
    def test_prefixo_multiplos(self):
        servico = ServicoCatalogo(schema_formulario=_schema_ouvidoria())
        txt = montar_prefixo_confirmacao(
            servico,
            {"o": "reclamacao", "q": "saude"},
        )
        self.assertIn("Tipo:", txt)
        self.assertIn("Área:", txt)