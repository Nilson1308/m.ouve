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

    def test_fallback_sem_chaves_tecnicas(self):
        fatos = coletar_fatos_operacionais("controladoria")
        conteudo = _fallback_conteudo(fatos, "controladoria")
        bruto = json.dumps(conteudo, ensure_ascii=False).lower()
        self.assertNotIn("motivo_hash", bruto)
        self.assertNotIn("fallback", bruto)
        for ins in conteudo.get("insights") or []:
            self.assertNotIn("=", ins.get("evidencia_numerica", ""))
            self.assertNotIn("Priorize acompanhamento", ins.get("recomendacao", ""))

    def test_acoes_distintas_por_detector(self):
        from atendimentos.services.agente_fallback_narrativa import insight_fallback_de_sinal

        a = insight_fallback_de_sinal(
            {
                "id": "critico_sem_campo",
                "detector": "critico_sem_campo",
                "categoria": "acao_imediata",
                "severidade": "critica",
                "titulo": "Críticos",
                "metricas": {"protocolos_exemplo": ["P-1"]},
            },
            "controladoria",
        )
        b = insight_fallback_de_sinal(
            {
                "id": "sla_vencido",
                "detector": "sla_vencido",
                "categoria": "acao_imediata",
                "severidade": "critica",
                "titulo": "SLA",
                "metricas": {"total_vencidos": 2},
            },
            "controladoria",
        )
        self.assertNotEqual(a["acao_sugerida"]["label"], b["acao_sugerida"]["label"])
        self.assertEqual(a["acao_sugerida"]["rota"], "/backoffice/protocolo/P-1")
        self.assertEqual(b["acao_sugerida"]["rota"], "/backoffice/relatorios/sla-cobrancas")

    def test_resolvido_nao_entra_diligencia_pendente(self):
        from atendimentos.models import DiligenciaProtocolo

        p_aberto = Protocolo.objects.create(
            codigo="P-DIL-AB",
            usuario=self.gestor_a,
            servico=self.servico,
            descricao="Aberto",
            status=Protocolo.Status.EM_ANDAMENTO,
        )
        p_fechado = Protocolo.objects.create(
            codigo="P-DIL-OK",
            usuario=self.gestor_a,
            servico=self.servico,
            descricao="Fechado",
            status=Protocolo.Status.RESOLVIDO,
        )
        for prot in (p_aberto, p_fechado):
            DiligenciaProtocolo.objects.create(
                protocolo=prot,
                unidade_solicitante=self.unidade_a,
                autor_servidor=self.gestor_a,
                pergunta="Envie foto",
                status=DiligenciaProtocolo.Status.RESPONDIDA,
                prazo_resposta=timezone.now() + timedelta(days=1),
                respondida_em=timezone.now(),
            )
        fatos = coletar_fatos_operacionais("unidade", unidade=self.unidade_a)
        sinal = next(
            (s for s in fatos["sinais"] if s.get("detector") == "diligencia_respondida_pendente"),
            None,
        )
        self.assertIsNotNone(sinal)
        codigos = sinal["metricas"].get("protocolos_exemplo") or []
        self.assertIn("P-DIL-AB", codigos)
        self.assertNotIn("P-DIL-OK", codigos)

    def test_cache_invalida_ao_resolver_protocolo(self):
        from atendimentos.services.agente_briefing_service import (
            _cache_key_briefing,
            invalidar_cache_briefing_protocolo,
        )

        cache.clear()
        b = gerar_briefing_escopo("controladoria", forcar=True)
        chave = _cache_key_briefing("controladoria", None, b.data_referencia)
        cache.set(chave, str(b.id), timeout=3600)
        p = Protocolo.objects.create(
            codigo="P-CACHE",
            usuario=self.gestor_a,
            servico=self.servico,
            descricao="x",
            status=Protocolo.Status.EM_ANALISE,
        )
        invalidar_cache_briefing_protocolo(p)
        self.assertIsNone(cache.get(chave))

    @override_settings(LLM_CHAT_API_KEY="test-key")
    @patch("atendimentos.llm_orchestrator._chamar_json_estruturado")
    def test_llm_usage_persiste_tokens(self, mock_json):
        from atendimentos.services.agente_briefing_service import _validar_conteudo_ia

        fatos_stub = {"sinais": [], "escopo_tipo": "controladoria"}
        conteudo = _fallback_conteudo(fatos_stub, "controladoria")

        def _fake(**kwargs):
            sink = kwargs.get("usage_sink")
            if sink is not None:
                sink[:] = [512, 256, False]
            return _validar_conteudo_ia(conteudo, fatos_stub)

        mock_json.side_effect = _fake
        cfg = ConfiguracaoAgenteGestao.load()
        cfg.agente_ativo = True
        cfg.orcamento_tokens_mensal = 9_999_999
        cfg.save()
        b = gerar_briefing_escopo("controladoria", forcar=True)
        self.assertEqual(b.modo_geracao, "llm")
        self.assertEqual(b.tokens_entrada, 512)
        self.assertEqual(b.tokens_saida, 256)

    def test_critico_unico_rota_protocolo(self):
        from atendimentos.services.agente_acoes import montar_acao_sugerida

        acao = montar_acao_sugerida(
            "critico_sem_campo",
            escopo_tipo="controladoria",
            metricas={"protocolos_exemplo": ["P-TRI-99"]},
        )
        self.assertEqual(acao["rota"], "/backoffice/protocolo/P-TRI-99")
        self.assertIn("P-TRI-99", acao["label"])

    def test_ouvidoria_sem_geo_nao_entra_mapa_calor(self):
        from django.contrib.gis.geos import Point

        from core_auth.models import EnderecoCidadao
        from atendimentos.services.mapa_calor_service import queryset_mapa_calor
        from atendimentos.services.protocolo_localidade import sincronizar_localidade_protocolo

        EnderecoCidadao.objects.create(
            usuario=self.gestor_a,
            logradouro="Rua Teste",
            numero="1",
            bairro="BairroResidencial",
            cidade="Mogi das Cruzes",
            estado="SP",
            cep="08700-000",
            localizacao=Point(-46.2, -23.5, srid=4326),
        )
        p = Protocolo.objects.create(
            codigo="P-GEO-LGPD",
            usuario=self.gestor_a,
            servico=self.servico,
            descricao="Reclamação administrativa sem local",
            status=Protocolo.Status.EM_ANALISE,
            dados_dinamicos={},
            origem_localizacao=Protocolo.OrigemLocalizacao.NENHUMA,
        )
        sincronizar_localidade_protocolo(p, persistir=True)
        p.refresh_from_db()
        self.assertNotEqual(
            (p.dados_dinamicos or {}).get("bairro", "").lower(),
            "bairroresidencial",
        )
        qs, _meta = queryset_mapa_calor(self.super, {})
        self.assertFalse(qs.filter(codigo="P-GEO-LGPD").exists())
        fatos = coletar_fatos_operacionais("controladoria")
        picos = [s for s in fatos["sinais"] if s.get("detector") == "pico_bairro"]
        for s in picos:
            codigos = s.get("metricas", {}).get("protocolos_exemplo") or []
            self.assertNotIn("P-GEO-LGPD", codigos)