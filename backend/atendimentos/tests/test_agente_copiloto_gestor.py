"""Sprint 4.7B — Copiloto Gestor (tools, API assíncrona, anti-IDOR)."""

import json
import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from atendimentos.models import ConfiguracaoAgenteGestao, MensagemCopilotoGestor, Protocolo, SessaoCopilotoGestor
from atendimentos.services.agente_briefing_service import obter_consumo_tokens_mes
from atendimentos.services.agente_copiloto_tools import (
    executar_tool,
    listar_anomalias_equipamentos_bairros,
)
from atendimentos.services.agente_copiloto_service import processar_mensagem_copiloto
from catalogo.models import CategoriaCatalogo, ServicoCatalogo, UnidadeAdministrativa
from core_auth.models import PerfilAcesso
from core_auth.rbac import aplicar_regras_automaticas, permissoes_padrao

User = get_user_model()


def _perfil_mesa_staff():
    base = permissoes_padrao()
    base["mesa_trabalho"] = {"ler": True, "criar": True, "editar": True, "excluir": False}
    base["regras"]["exige_unidade"] = True
    base["regras"]["acesso_staff"] = True
    return aplicar_regras_automaticas(base)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class AgenteCopilotoGestorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.unidade_a = UnidadeAdministrativa.objects.create(
            nome="Secretaria A", sigla="SEC-A", ativo=True
        )
        cls.unidade_b = UnidadeAdministrativa.objects.create(
            nome="Secretaria B", sigla="SEC-B", ativo=True
        )
        cat = CategoriaCatalogo.objects.create(
            nome="Cat", slug="cat-cop", tipo_legado="zeladoria", ativo=True
        )
        cls.servico_a = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Serv A",
            unidade_responsavel=cls.unidade_a,
            schema_formulario={"type": "object", "properties": {}},
            ativo=True,
            sla_horas=24,
        )
        cls.servico_b = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Serv B",
            unidade_responsavel=cls.unidade_b,
            schema_formulario={"type": "object", "properties": {}},
            ativo=True,
            sla_horas=24,
        )
        perfil = PerfilAcesso.objects.create(
            codigo="gestor_cop_a",
            nome="Gestor A",
            permissoes=_perfil_mesa_staff(),
            ativo=True,
        )
        cls.gestor_a = User.objects.create_user(
            cpf="44444444444",
            password="x",
            nome="Gestor A Cop",
            email="gestor-cop-a@test.local",
            unidade=cls.unidade_a,
            is_staff=True,
        )
        cls.gestor_a.perfil_acesso = perfil
        cls.gestor_a.save()
        cls.gestor_b = User.objects.create_user(
            cpf="55555555555",
            password="x",
            nome="Gestor B Cop",
            email="gestor-cop-b@test.local",
            unidade=cls.unidade_b,
            is_staff=True,
        )
        cls.gestor_b.perfil_acesso = perfil
        cls.gestor_b.save()
        cls.super = User.objects.create_user(
            cpf="66666666666",
            password="x",
            nome="Super Cop",
            email="super-cop@test.local",
            is_staff=True,
        )
        PerfilAcesso.objects.create(
            codigo="super_cop_test",
            nome="Super",
            permissoes={"regras": {"super_admin": True, "acesso_staff": True}},
        )
        cls.super.perfil_acesso = PerfilAcesso.objects.get(codigo="super_cop_test")
        cls.super.save()

        Protocolo.objects.create(
            codigo="P-COP-A1",
            usuario=cls.gestor_a,
            servico=cls.servico_a,
            descricao="Teste unidade A",
            status=Protocolo.Status.EM_ANALISE,
            origem_localizacao=Protocolo.OrigemLocalizacao.NENHUMA,
        )
        Protocolo.objects.create(
            codigo="P-COP-B1",
            usuario=cls.gestor_b,
            servico=cls.servico_b,
            descricao="Teste unidade B",
            status=Protocolo.Status.EM_ANALISE,
            origem_localizacao=Protocolo.OrigemLocalizacao.NENHUMA,
        )

    def test_tool_anti_idor_unidade(self):
        eff_a = executar_tool(
            "obter_resumo_eficiencia",
            self.gestor_a,
            {"unidade_id": str(self.unidade_b.id), "periodo_dias": 30},
        )
        self.assertEqual(eff_a.get("escopo_aplicado"), "unidade")
        self.assertTrue(eff_a.get("unidade_forcada_escopo"))
        eff_b = executar_tool(
            "obter_resumo_eficiencia",
            self.gestor_b,
            {"periodo_dias": 30},
        )
        self.assertGreaterEqual(eff_b.get("total_abertos", 0), 1)
        abertos_super = executar_tool(
            "obter_resumo_eficiencia",
            self.super,
            {"periodo_dias": 30},
        )
        self.assertGreaterEqual(abertos_super.get("total_abertos", 0), 2)

    def test_geo_higiene_sem_nenhuma(self):
        out = listar_anomalias_equipamentos_bairros(self.super, periodo_dias=14)
        bruto = json.dumps(out, ensure_ascii=False)
        self.assertNotIn("nenhuma", bruto.lower())
        self.assertTrue(out.get("somente_origem_localizacao_ocorrencia"))

    def test_sessao_404_outro_usuario(self):
        sessao = SessaoCopilotoGestor.objects.create(
            usuario=self.gestor_a,
            titulo="Privada",
            perspectiva="unidade",
            unidade=self.unidade_a,
        )
        client = APIClient()
        client.force_authenticate(self.gestor_b)
        resp = client.get(f"/api/v1/backoffice/agente/copiloto/sessoes/{sessao.id}")
        self.assertEqual(resp.status_code, 404)

    def test_copiloto_desativado_403(self):
        cfg = ConfiguracaoAgenteGestao.load()
        cfg.copiloto_chat_ativo = False
        cfg.save()
        client = APIClient()
        client.force_authenticate(self.super)
        resp = client.post(
            "/api/v1/backoffice/agente/copiloto/perguntar",
            {"pergunta": "Resumo da fila operacional"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)
        cfg.copiloto_chat_ativo = True
        cfg.save()

    def test_cota_diaria_429(self):
        cfg = ConfiguracaoAgenteGestao.load()
        cfg.limite_perguntas_dia_por_usuario = 1
        cfg.save()
        client = APIClient()
        client.force_authenticate(self.super)
        r1 = client.post(
            "/api/v1/backoffice/agente/copiloto/perguntar",
            {"pergunta": "Como está a fila?"},
            format="json",
        )
        self.assertEqual(r1.status_code, 202)
        r2 = client.post(
            "/api/v1/backoffice/agente/copiloto/perguntar",
            {"pergunta": "E os SLA vencidos?"},
            format="json",
        )
        self.assertEqual(r2.status_code, 429)
        cfg.limite_perguntas_dia_por_usuario = 30
        cfg.save()

    @patch("atendimentos.llm_orchestrator._chamar_json_estruturado")
    def test_fluxo_assincrono_mock_llm(self, mock_llm):
        calls = {"n": 0}

        def _side_effect(*_args, **kwargs):
            sink = kwargs.get("usage_sink")
            if sink is not None:
                sink[:] = [100, 60, False]
            calls["n"] += 1
            if calls["n"] == 1:
                return {"tools": [{"nome": "resumir_fila_operacional", "parametros": {}}]}
            return {"resposta": "A fila operacional apresenta volume moderado; use a Mesa para agir."}

        mock_llm.side_effect = _side_effect
        client = APIClient()
        client.force_authenticate(self.super)
        resp = client.post(
            "/api/v1/backoffice/agente/copiloto/perguntar",
            {"pergunta": "Resumo da fila operacional hoje"},
            format="json",
        )
        self.assertEqual(resp.status_code, 202)
        sessao_id = resp.data["sessao_id"]
        processar_mensagem_copiloto(resp.data["mensagem_assistente_id"])
        det = client.get(f"/api/v1/backoffice/agente/copiloto/sessoes/{sessao_id}")
        self.assertEqual(det.status_code, 200)
        self.assertFalse(det.data.get("ia_processando"))
        assistente = [
            m for m in det.data["mensagens"] if m["papel"] == "assistente"
        ][-1]
        self.assertEqual(assistente["status_processamento"], "concluida")
        self.assertTrue(assistente.get("ferramentas_usadas"))
        self.assertIsInstance(assistente.get("referencias"), list)
        self.assertGreater(assistente.get("tokens_entrada", 0) + assistente.get("tokens_saida", 0), 0)
        consumo_antes = obter_consumo_tokens_mes()
        self.assertGreaterEqual(consumo_antes, assistente["tokens_entrada"] + assistente["tokens_saida"])

    def test_llm_payload_sem_pii(self):
        sessao = SessaoCopilotoGestor.objects.create(
            usuario=self.gestor_a,
            titulo="Pergunta",
            perspectiva="unidade",
            unidade=self.unidade_a,
        )
        MensagemCopilotoGestor.objects.create(
            sessao=sessao,
            papel=MensagemCopilotoGestor.Papel.USUARIO,
            conteudo="Situação da fila?",
        )
        msg_ass = MensagemCopilotoGestor.objects.create(
            sessao=sessao,
            papel=MensagemCopilotoGestor.Papel.ASSISTENTE,
            conteudo="",
            status_processamento=MensagemCopilotoGestor.StatusProcessamento.PROCESSANDO,
        )
        payloads = []

        def _captura(*args, **kwargs):
            for m in kwargs.get("mensagens") or []:
                payloads.append(m.get("content") or "")
            if len(payloads) <= 1:
                return {"tools": [{"nome": "obter_resumo_eficiencia", "parametros": {}}]}
            return {"resposta": "Resumo sem dados pessoais."}

        with patch("atendimentos.llm_orchestrator._chamar_json_estruturado", side_effect=_captura):
            processar_mensagem_copiloto(str(msg_ass.id))

        bruto = json.dumps(payloads, ensure_ascii=False).lower()
        self.assertNotIn(self.gestor_a.cpf, bruto)
        self.assertNotIn("gestor-cop-a@test", bruto)
        self.assertNotIn("@test.local", bruto)

    def test_fallback_quando_sintese_llm_falha(self):
        sessao = SessaoCopilotoGestor.objects.create(
            usuario=self.super,
            titulo="SLA",
            perspectiva="controladoria",
        )
        MensagemCopilotoGestor.objects.create(
            sessao=sessao,
            papel=MensagemCopilotoGestor.Papel.USUARIO,
            conteudo="Como estão os SLA vencidos?",
        )
        msg_ass = MensagemCopilotoGestor.objects.create(
            sessao=sessao,
            papel=MensagemCopilotoGestor.Papel.ASSISTENTE,
            conteudo="",
            status_processamento=MensagemCopilotoGestor.StatusProcessamento.PROCESSANDO,
        )
        calls = {"n": 0}

        def _side(*_a, **_kw):
            calls["n"] += 1
            if calls["n"] == 1:
                return {"tools": [{"nome": "resumir_fila_operacional"}]}
            from atendimentos.llm_orchestrator import ChatOrchestrationError

            raise ChatOrchestrationError(
                "Falha ao consultar o modelo: Error code: 400 - Failed to validate JSON."
            )

        with patch("atendimentos.llm_orchestrator._chamar_json_estruturado", side_effect=_side):
            processar_mensagem_copiloto(str(msg_ass.id))

        msg_ass.refresh_from_db()
        self.assertEqual(msg_ass.status_processamento, "concluida")
        self.assertEqual(msg_ass.modo_geracao, "deterministico_fallback")
        self.assertIn("Fila operacional", msg_ass.conteudo)
        self.assertNotIn("Failed to validate JSON", msg_ass.conteudo)