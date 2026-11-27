"""Sprint 4.9 — modo de abertura híbrida PWA, catálogo guiado e telemetria."""

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from atendimentos.chat_estado import FaseChat, get_fase, get_meta
from atendimentos.chat_services import finalizar_sessao_com_protocolo
from atendimentos.models import ConfiguracaoSistema, Protocolo, SessaoChat
from atendimentos.pwa_abertura import (
    CODE_SERVICO_OBRIGATORIO_GUIADO,
    MODO_ABERTURA_CATALOGO_GUIADO,
    MODO_ABERTURA_CHAT_IA,
    MODO_ABERTURA_HIBRIDO,
    ORIGEM_ABERTURA_CATALOGO_GUIADO,
    ORIGEM_ABERTURA_CHAT_IA,
)
from atendimentos.services.analytics_service import calcular_origem_abertura_resumo
from catalogo.models import CategoriaCatalogo, ServicoCatalogo, UnidadeAdministrativa
from catalogo.pwa_catalogo import PWA_CONFIG_CACHE_KEY, invalidar_cache_config_pwa
from core_auth.models import PerfilAcesso
from core_auth.rbac import aplicar_regras_automaticas, permissoes_padrao

User = get_user_model()


def _perms_configuracoes():
    base = permissoes_padrao()
    base["configuracoes"] = {k: True for k in ("ler", "criar", "editar", "excluir")}
    base["regras"]["super_admin"] = True
    return aplicar_regras_automaticas(base)


SCHEMA_SIMPLES = {
    "type": "object",
    "properties": {
        "descricao": {"type": "string", "title": "Descreva o problema", "minLength": 5},
    },
    "required": ["descricao"],
    "$metadata": {"ordem_campos": ["descricao"]},
}


class ModoAberturaPwaBaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.unidade = UnidadeAdministrativa.objects.create(nome="Sec Teste", sigla="ST", ativo=True)
        cls.cat_ab = CategoriaCatalogo.objects.create(
            nome="Categoria AB", slug="categoria-ab", ativo=True
        )
        cls.cat_unica = CategoriaCatalogo.objects.create(
            nome="Categoria Unica", slug="categoria-unica", ativo=True
        )
        agora = timezone.now()
        cls.serv_a = ServicoCatalogo.objects.create(
            categoria=cls.cat_ab,
            nome="Serviço A",
            unidade_responsavel=cls.unidade,
            schema_formulario=SCHEMA_SIMPLES,
            ativo=True,
            publicado_em=agora,
            visivel_catalogo_pwa=True,
            ordem_exibicao_pwa=10,
        )
        cls.serv_b = ServicoCatalogo.objects.create(
            categoria=cls.cat_ab,
            nome="Serviço B",
            unidade_responsavel=cls.unidade,
            schema_formulario=SCHEMA_SIMPLES,
            ativo=True,
            publicado_em=agora,
            visivel_catalogo_pwa=True,
            ordem_exibicao_pwa=20,
        )
        cls.serv_oculto = ServicoCatalogo.objects.create(
            categoria=cls.cat_ab,
            nome="Interno",
            unidade_responsavel=cls.unidade,
            schema_formulario=SCHEMA_SIMPLES,
            ativo=True,
            publicado_em=agora,
            visivel_catalogo_pwa=False,
        )
        cls.serv_unico = ServicoCatalogo.objects.create(
            categoria=cls.cat_unica,
            nome="Único",
            unidade_responsavel=cls.unidade,
            schema_formulario=SCHEMA_SIMPLES,
            ativo=True,
            publicado_em=agora,
            visivel_catalogo_pwa=True,
        )
        cls.cidadao = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Cidadao PWA",
            email="cidadao.pwa@test.local",
        )
        cls.perfil_gestor = PerfilAcesso.objects.create(
            codigo="teste_pwa_cfg",
            nome="Gestor CFG",
            permissoes=_perms_configuracoes(),
            ativo=True,
        )
        cls.gestor = User.objects.create_user(
            cpf="52998224725",
            password="x",
            nome="Gestor Config",
            email="gestor.pwa@test.local",
            perfil_acesso=cls.perfil_gestor,
            is_staff=True,
        )
        cfg = ConfiguracaoSistema.load()
        cfg.modo_abertura_pwa = MODO_ABERTURA_HIBRIDO
        cfg.save(update_fields=["modo_abertura_pwa"])

    def setUp(self):
        cache.clear()
        invalidar_cache_config_pwa()


class ConfigPwaPublicTests(ModoAberturaPwaBaseTestCase):
    def test_config_pwa_modo_e_servico_unico(self):
        client = APIClient()
        resp = client.get("/api/v1/catalogo/config-pwa")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["modo_abertura_pwa"], MODO_ABERTURA_HIBRIDO)
        cat_ab = next(c for c in resp.data["categorias"] if c["slug"] == "categoria-ab")
        self.assertEqual(cat_ab["total_servicos_visiveis"], 2)
        self.assertIsNone(cat_ab["servico_unico_id"])
        cat_u = next(c for c in resp.data["categorias"] if c["slug"] == "categoria-unica")
        self.assertEqual(cat_u["total_servicos_visiveis"], 1)
        self.assertEqual(cat_u["servico_unico_id"], str(self.serv_unico.id))

    def test_listagem_pwa_oculta_nao_visivel(self):
        client = APIClient()
        resp = client.get(
            "/api/v1/catalogo/servicos",
            {"categoria": "categoria-ab", "apenas_visiveis_pwa": "true"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        nomes = {s["nome"] for s in resp.data["servicos"]}
        self.assertIn("Serviço A", nomes)
        self.assertNotIn("Interno", nomes)


class SessaoCatalogoGuiadoTests(ModoAberturaPwaBaseTestCase):
    @patch("atendimentos.slot_filling_service.aplicar_slot_filling_abertura", return_value=("", {}))
    def test_post_sessao_servico_id_pula_classificacao(self, _mock_slot):
        client = APIClient()
        client.force_authenticate(user=self.cidadao)
        with patch(
            "atendimentos.llm_orchestrator.LLMOrchestrator._estagio_classificacao"
        ) as mock_cls:
            mock_cls.side_effect = AssertionError("classificador não deve ser chamado")
            resp = client.post(
                "/api/v1/chat/sessao",
                {"categoria_inicial": "categoria-ab", "servico_id": str(self.serv_a.id)},
                format="json",
            )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        sessao = SessaoChat.objects.get(pk=resp.data["sessao"]["id"])
        self.assertEqual(sessao.origem_abertura, ORIGEM_ABERTURA_CATALOGO_GUIADO)
        self.assertEqual(sessao.servico_identificado_id, self.serv_a.id)
        self.assertEqual(get_fase(sessao), FaseChat.PREENCHIMENTO)
        msg = resp.data["mensagem"]
        self.assertIn("Serviço A", msg["conteudo_texto"])
        self.assertEqual(msg.get("tipo_acao"), None)

    @patch("atendimentos.slot_filling_service.aplicar_slot_filling_abertura", return_value=("", {}))
    def test_protocolo_herda_origem_abertura(self, _mock_slot):
        client = APIClient()
        client.force_authenticate(user=self.cidadao)
        resp = client.post(
            "/api/v1/chat/sessao",
            {"categoria_inicial": "categoria-ab", "servico_id": str(self.serv_a.id)},
            format="json",
        )
        sessao = SessaoChat.objects.get(pk=resp.data["sessao"]["id"])
        sessao.dados_coletados = {
            **(sessao.dados_coletados or {}),
            "descricao": "Problema relatado pelo cidadão no teste.",
        }
        sessao.save(update_fields=["dados_coletados", "atualizado_em"])
        protocolo = finalizar_sessao_com_protocolo(sessao)
        self.assertEqual(protocolo.origem_abertura, ORIGEM_ABERTURA_CATALOGO_GUIADO)


class ModoCatalogoGuiadoObrigatorioTests(ModoAberturaPwaBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cfg = ConfiguracaoSistema.load()
        cfg.modo_abertura_pwa = MODO_ABERTURA_CATALOGO_GUIADO
        cfg.save(update_fields=["modo_abertura_pwa"])

    def test_rejeita_multiplos_servicos_sem_servico_id(self):
        client = APIClient()
        client.force_authenticate(user=self.cidadao)
        resp = client.post(
            "/api/v1/chat/sessao",
            {"categoria_inicial": "categoria-ab"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["error"]["code"], CODE_SERVICO_OBRIGATORIO_GUIADO)

    @patch("atendimentos.slot_filling_service.aplicar_slot_filling_abertura", return_value=("", {}))
    def test_auto_seleciona_categoria_com_um_servico(self, _mock_slot):
        client = APIClient()
        client.force_authenticate(user=self.cidadao)
        resp = client.post(
            "/api/v1/chat/sessao",
            {"categoria_inicial": "categoria-unica"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            resp.data["sessao"]["origem_abertura"],
            ORIGEM_ABERTURA_CATALOGO_GUIADO,
        )
        self.assertEqual(
            str(resp.data["sessao"]["servico_identificado"]["id"]),
            str(self.serv_unico.id),
        )


class ConfiguracaoBackofficePwaTests(ModoAberturaPwaBaseTestCase):
    def test_patch_modo_invalida_cache(self):
        cache.set(PWA_CONFIG_CACHE_KEY, {"modo_abertura_pwa": "stale"}, timeout=60)
        client = APIClient()
        client.force_authenticate(user=self.gestor)
        resp = client.patch(
            "/api/v1/backoffice/configuracoes/atendimento-pwa",
            {"modo_abertura_pwa": MODO_ABERTURA_CHAT_IA},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNone(cache.get(PWA_CONFIG_CACHE_KEY))

    def test_patch_requer_configuracoes(self):
        sem_perm = User.objects.create_user(
            cpf="11144477735",
            password="x",
            nome="Sem Perm",
            email="sem@test.local",
        )
        client = APIClient()
        client.force_authenticate(user=sem_perm)
        resp = client.patch(
            "/api/v1/backoffice/configuracoes/atendimento-pwa",
            {"modo_abertura_pwa": MODO_ABERTURA_CHAT_IA},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class OrigemAberturaAnalyticsTests(ModoAberturaPwaBaseTestCase):
    def test_resumo_respeita_contagens(self):
        p_ia = Protocolo.objects.create(
            codigo="P-IA-01",
            usuario=self.cidadao,
            servico=self.serv_a,
            descricao="Via IA",
            status=Protocolo.Status.RESOLVIDO,
            origem_abertura=ORIGEM_ABERTURA_CHAT_IA,
        )
        p_cat = Protocolo.objects.create(
            codigo="P-CAT-01",
            usuario=self.cidadao,
            servico=self.serv_b,
            descricao="Via catálogo",
            status=Protocolo.Status.RESOLVIDO,
            origem_abertura=ORIGEM_ABERTURA_CATALOGO_GUIADO,
        )
        p_ia.data_atualizacao = p_ia.data_criacao + timedelta(hours=2)
        p_cat.data_atualizacao = p_cat.data_criacao + timedelta(hours=4)
        Protocolo.objects.filter(pk=p_ia.pk).update(data_atualizacao=p_ia.data_atualizacao)
        Protocolo.objects.filter(pk=p_cat.pk).update(data_atualizacao=p_cat.data_atualizacao)

        qs = Protocolo.objects.filter(codigo__in=["P-IA-01", "P-CAT-01"])
        resumo = calcular_origem_abertura_resumo(qs)
        self.assertEqual(resumo[ORIGEM_ABERTURA_CHAT_IA]["total_protocolos"], 1)
        self.assertEqual(resumo[ORIGEM_ABERTURA_CATALOGO_GUIADO]["total_protocolos"], 1)
        self.assertEqual(resumo[ORIGEM_ABERTURA_CHAT_IA]["percentual"], 50.0)
        self.assertEqual(resumo[ORIGEM_ABERTURA_CATALOGO_GUIADO]["tma_horas"], 4.0)