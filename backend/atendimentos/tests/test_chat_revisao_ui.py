from unittest.mock import MagicMock, patch

from django.test import TestCase

from atendimentos.chat_services import _sincronizar_turno_revisao
from atendimentos.llm_orchestrator import MSG_REVISAO, TurnResult


class SincronizarTurnoRevisaoTests(TestCase):
    @patch("atendimentos.chat_services._requisitos_revisao_ok", return_value=False)
    @patch("atendimentos.chat_services._anexo_sessao_obrigatorio", return_value=True)
    @patch("atendimentos.chat_services._localizacao_ok", return_value=True)
    @patch("atendimentos.chat_services.set_meta")
    def test_nao_mantem_texto_resumo_sem_foto(
        self, _set_meta, _loc_ok, _anexo_obrig, _requisitos
    ):
        servico = MagicMock()
        servico.exige_localizacao = False
        sessao = MagicMock()
        sessao.servico_identificado = servico
        turno = TurnResult(
            resposta_cidadao=MSG_REVISAO,
            acao_ui="revisao_final",
            ir_para_revisao=True,
        )
        with patch("atendimentos.chat_services._msg_foto_servico", return_value="Envie uma foto."):
            _sincronizar_turno_revisao(sessao, turno)
        self.assertEqual(turno.acao_ui, "solicitar_foto")
        self.assertEqual(turno.resposta_cidadao, "Envie uma foto.")
        self.assertFalse(turno.ir_para_revisao)

    @patch("atendimentos.chat_services._requisitos_revisao_ok", return_value=True)
    @patch("atendimentos.chat_services.set_meta")
    def test_revisao_ok_mantem_acao_ui(self, _set_meta, _requisitos):
        sessao = MagicMock()
        sessao.servico_identificado = MagicMock()
        turno = TurnResult(resposta_cidadao=MSG_REVISAO, acao_ui="revisao_final")
        _sincronizar_turno_revisao(sessao, turno)
        self.assertEqual(turno.acao_ui, "revisao_final")