"""Sprint 4.7A — Radar proativo, budget cap e digest."""

import json
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from atendimentos.models import (
    BriefingOperacionalIA,
    ConfiguracaoAgenteGestao,
    ConfiguracaoSlaCobranca,
    Protocolo,
)
from atendimentos.services.agente_briefing_service import (
    _fallback_conteudo,
    gerar_briefing_escopo,
    obter_consumo_tokens_mes,
)
from atendimentos.services.agente_persona import resolver_escopo_briefing_usuario
from atendimentos.services.agente_sinais_service import coletar_fatos_operacionais
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


class AgenteRadarProativoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.unidade_a = UnidadeAdministrativa.objects.create(
            nome="Secretaria A", sigla="SEC-A", ativo=True
        )
        cls.unidade_b = UnidadeAdministrativa.objects.create(
            nome="Secretaria B", sigla="SEC-B", ativo=True
        )
        cat = CategoriaCatalogo.objects.create(
            nome="Cat", slug="cat-ag", tipo_legado="zeladoria", ativo=True
        )
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Serv",
            unidade_responsavel=cls.unidade_a,
            schema_formulario={"type": "object", "properties": {}},
            ativo=True,
            sla_horas=24,
        )
        perfil_gestor = PerfilAcesso.objects.create(
            codigo="gestor_a_agente",
            nome="Gestor A",
            permissoes=_perfil_mesa_staff(),
            ativo=True,
        )
        cls.gestor_a = User.objects.create_user(
            cpf="11111111111",
            password="x",
            nome="Gestor A",
            email="gestor-a@test.local",
            unidade=cls.unidade_a,
            is_staff=True,
        )
        cls.gestor_a.perfil_acesso = perfil_gestor
        cls.gestor_a.save()
        cls.gestor_b = User.objects.create_user(
            cpf="22222222222",
            password="x",
            nome="Gestor B",
            email="gestor-b@test.local",
            unidade=cls.unidade_b,
        )
        cls.super = User.objects.create_user(
            cpf="33333333333",
            password="x",
            nome="Super",
            email="super@test.local",
            is_staff=True,
        )
        PerfilAcesso.objects.create(
            codigo="super_admin_ag_test",
            nome="Super",
            permissoes={"regras": {"super_admin": True, "acesso_staff": True}},
        )
        cls.super.perfil_acesso = PerfilAcesso.objects.get(codigo="super_admin_ag_test")
        cls.super.save()

    def test_fatos_sem_pii(self):
        Protocolo.objects.create(
            codigo="P-AG-001",
            usuario=self.gestor_a,
            servico=self.servico,
            descricao="Buraco na via",
            status=Protocolo.Status.EM_ANALISE,
            urgencia=Protocolo.Urgencia.CRITICA,
        )
        fatos = coletar_fatos_operacionais("controladoria")
        bruto = json.dumps(fatos, ensure_ascii=False).lower()
        self.assertNotIn(self.gestor_a.cpf, bruto)
        self.assertNotIn("gestor-a@test", bruto)

    def test_anti_idor_gestor_nao_ve_controladoria(self):
        escopo, _ = resolver_escopo_briefing_usuario(self.gestor_a, {})
        self.assertEqual(escopo, "unidade")
        briefing_ctrl = gerar_briefing_escopo("controladoria")
        client = APIClient()
        client.force_authenticate(self.gestor_a)
        resp = client.get("/api/v1/backoffice/agente/briefing")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["escopo_tipo"], "unidade")
        self.assertNotEqual(resp.data["briefing_id"], str(briefing_ctrl.id))
        aval = client.post(
            f"/api/v1/backoffice/agente/briefing/{briefing_ctrl.id}/avaliar",
            {"insight_id": "i1", "util": True},
            format="json",
        )
        self.assertEqual(aval.status_code, 403)

    def test_fallback_budget_cap(self):
        cfg = ConfiguracaoAgenteGestao.load()
        cfg.orcamento_tokens_mensal = 100
        cfg.agente_ativo = True
        cfg.save()
        BriefingOperacionalIA.objects.create(
            escopo_tipo="controladoria",
            data_referencia=timezone.localdate(),
            tokens_entrada=80,
            tokens_saida=30,
        )
        self.assertGreaterEqual(obter_consumo_tokens_mes(), 110)
        with patch.dict("os.environ", {}, clear=False):
            with patch(
                "atendimentos.services.agente_briefing_service._chamar_llm_briefing",
                side_effect=AssertionError("LLM não deve rodar"),
            ):
                b = gerar_briefing_escopo("ouvidoria", forcar=True)
        self.assertEqual(b.modo_geracao, "deterministico_fallback")

    @override_settings(LLM_CHAT_API_KEY="test-key")
    @patch("atendimentos.services.agente_briefing_service._chamar_llm_briefing")
    def test_llm_mock_grava_tokens(self, mock_llm):
        mock_llm.return_value = (
            _fallback_conteudo({"sinais": [], "escopo_tipo": "controladoria"}, "controladoria"),
            1200,
            800,
            "mock-model",
        )
        cfg = ConfiguracaoAgenteGestao.load()
        cfg.agente_ativo = True
        cfg.orcamento_tokens_mensal = 9_999_999
        cfg.save()
        b = gerar_briefing_escopo("controladoria", forcar=True)
        self.assertEqual(b.modo_geracao, "llm")
        self.assertEqual(b.tokens_entrada, 1200)

    def test_rate_limit_forcar(self):
        cache.clear()
        client = APIClient()
        client.force_authenticate(self.super)
        r1 = client.get("/api/v1/backoffice/agente/briefing", {"forcar": "true"})
        self.assertEqual(r1.status_code, 200)
        r2 = client.get("/api/v1/backoffice/agente/briefing", {"forcar": "true"})
        self.assertEqual(r2.status_code, 429)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_digest_inclui_radar_quando_ativo(self):
        cfg_sla = ConfiguracaoSlaCobranca.load()
        cfg_sla.emails_controladoria = ["ctrl-digest@test.local"]
        cfg_sla.save()
        cfg_ag = ConfiguracaoAgenteGestao.load()
        cfg_ag.incluir_resumo_no_digest_email = True
        cfg_ag.agente_ativo = True
        cfg_ag.save()
        gerar_briefing_escopo("controladoria", forcar=True)
        p = Protocolo.objects.create(
            codigo="P-DIG-1",
            usuario=self.gestor_a,
            servico=self.servico,
            dados_dinamicos={},
            descricao="Atraso",
            status=Protocolo.Status.EM_ANALISE,
        )
        Protocolo.objects.filter(pk=p.pk).update(
            data_criacao=timezone.now() - timedelta(hours=48)
        )
        from atendimentos.services.sla_cobranca_service import enviar_digest_sla_atrasados

        mail.outbox.clear()
        enviar_digest_sla_atrasados(incluir_controladoria=True)
        self.assertTrue(mail.outbox)
        corpo = mail.outbox[-1].body
        self.assertIn("Radar IA", corpo)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_digest_omite_radar_quando_desligado(self):
        cfg_sla = ConfiguracaoSlaCobranca.load()
        cfg_sla.emails_controladoria = ["ctrl2@test.local"]
        cfg_sla.save()
        cfg_ag = ConfiguracaoAgenteGestao.load()
        cfg_ag.incluir_resumo_no_digest_email = False
        cfg_ag.save()
        p = Protocolo.objects.create(
            codigo="P-DIG-2",
            usuario=self.gestor_a,
            servico=self.servico,
            dados_dinamicos={},
            descricao="Atraso",
            status=Protocolo.Status.EM_ANALISE,
        )
        Protocolo.objects.filter(pk=p.pk).update(
            data_criacao=timezone.now() - timedelta(hours=48)
        )
        from atendimentos.services.sla_cobranca_service import enviar_digest_sla_atrasados

        mail.outbox.clear()
        enviar_digest_sla_atrasados(incluir_controladoria=True)
        self.assertTrue(mail.outbox)
        self.assertNotIn("Radar IA", mail.outbox[-1].body)