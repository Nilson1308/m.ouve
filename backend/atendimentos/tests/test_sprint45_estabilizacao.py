"""Sprint 4.5 — magic link GET, higiene notificações chat, busca governança."""

import json
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from atendimentos.chat_services import executar_processamento_ia
from atendimentos.llm_orchestrator import TurnResult
from atendimentos.magic_link_services import gerar_magic_link_ordem
from atendimentos.management.commands.limpar_notificacoes_chat_rag import (
    queryset_notificacoes_chat_rag,
)
from atendimentos.models import (
    AnexoProtocolo,
    DiligenciaProtocolo,
    MensagemChat,
    NotificacaoCidadao,
    OrdemServico,
    Protocolo,
    ReaberturaProtocolo,
    SessaoChat,
)
from atendimentos.notificacoes_cidadao import notificar_status_protocolo
from catalogo.models import CategoriaCatalogo, ServicoCatalogo, UnidadeAdministrativa
from core_auth.models import PerfilAcesso
from core_auth.rbac import aplicar_regras_automaticas, permissoes_padrao

User = get_user_model()

PII_MARKERS = ("52998224725", "cid.", "@test.local", "Cidadão", "cpf", "telefone")


def _perms_super():
    base = permissoes_padrao()
    base["configuracoes"] = {k: True for k in ("ler", "criar", "editar", "excluir")}
    base["gestao_usuarios"] = {k: True for k in ("ler", "criar", "editar", "excluir")}
    base["regras"]["super_admin"] = True
    return aplicar_regras_automaticas(base)


class MagicLinkContextoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.unidade = UnidadeAdministrativa.objects.create(
            nome="Obras Campo", sigla="OBR", ativo=True
        )
        cat = CategoriaCatalogo.objects.create(nome="Zel", slug="zel-magic", ativo=True)
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Buraco",
            unidade_responsavel=cls.unidade,
            ativo=True,
        )
        cls.cidadao = User.objects.create_user(
            cpf="52998224725",
            password="x",
            nome="Maria Cidada Teste",
            email="maria.cid@test.local",
            telefone="11999998888",
        )
        cls.protocolo = Protocolo.objects.create(
            codigo="PROT-ML-45",
            usuario=cls.cidadao,
            servico=cls.servico,
            descricao="Buraco profundo na via.",
            endereco_texto="Av. Teste, 100",
            status=Protocolo.Status.EM_ANDAMENTO,
        )
        cls.ordem = OrdemServico.objects.create(
            protocolo=cls.protocolo,
            unidade=cls.unidade,
            status=OrdemServico.Status.EM_ANDAMENTO,
            despacho_tecnico="Tampar com CBUQ.",
            descricao="Despacho ouvidoria",
        )
        gerar_magic_link_ordem(cls.ordem)
        cls.token = cls.ordem.magic_link_token

    def setUp(self):
        self.client = APIClient()

    def test_get_contexto_sem_pii(self):
        AnexoProtocolo.objects.create(protocolo=self.protocolo, tipo_mime="image/jpeg")
        url = f"/api/v1/publico/evidencias/{self.token}"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["numero_protocolo"], "PROT-ML-45")
        self.assertIn("anexos_iniciais", resp.data)
        self.assertGreaterEqual(len(resp.data["anexos_iniciais"]), 1)

        texto = json.dumps(resp.data, ensure_ascii=False).lower()
        for marker in PII_MARKERS:
            self.assertNotIn(marker.lower(), texto)

    def test_get_token_expirado_410(self):
        self.ordem.magic_link_expira_em = timezone.now() - timedelta(hours=1)
        self.ordem.save(update_fields=["magic_link_expira_em"])
        url = f"/api/v1/publico/evidencias/{self.token}"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_410_GONE)

    def test_get_diligencia_com_anexos(self):
        anexo = AnexoProtocolo.objects.create(protocolo=self.protocolo, tipo_mime="image/png")
        d = DiligenciaProtocolo.objects.create(
            protocolo=self.protocolo,
            ordem_servico=self.ordem,
            unidade_solicitante=self.unidade,
            autor_servidor=self.cidadao,
            pergunta="Envie foto atualizada.",
            prazo_resposta=timezone.now() + timedelta(days=3),
            status=DiligenciaProtocolo.Status.RESPONDIDA,
            anexos_ids=[str(anexo.id)],
            resposta_cidadao="Segue em anexo.",
            respondida_em=timezone.now(),
        )
        url = f"/api/v1/publico/evidencias/{self.token}"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [x["id"] for x in resp.data["diligencias"]]
        self.assertIn(str(d.id), ids)
        item = next(x for x in resp.data["diligencias"] if x["id"] == str(d.id))
        self.assertTrue(item["anexos"])

    def test_motivo_reabertura_quando_os_da_reabertura(self):
        reab = ReaberturaProtocolo.objects.create(
            protocolo=self.protocolo,
            solicitante=self.cidadao,
            motivo="Serviço incompleto.",
            ordem_servico_criada=self.ordem,
        )
        url = f"/api/v1/publico/evidencias/{self.token}"
        resp = self.client.get(url)
        self.assertEqual(resp.data["motivo_reabertura"], reab.motivo)


class ChatRagNotificacoesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cat = CategoriaCatalogo.objects.create(nome="Cat", slug="cat-rag", ativo=True)
        unidade = UnidadeAdministrativa.objects.create(nome="UA", sigla="UA", ativo=True)
        servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Serv",
            unidade_responsavel=unidade,
            ativo=True,
        )
        cls.cidadao = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Cid RAG",
            email="rag@test.local",
        )
        cls.sessao = SessaoChat.objects.create(
            usuario=cls.cidadao,
            categoria_inicial="zeladoria",
            dados_coletados={"_meta": {"fase": "exploracao"}},
        )
        cls.protocolo = Protocolo.objects.create(
            codigo="PROT-RAG-1",
            usuario=cls.cidadao,
            servico=servico,
            descricao="Teste",
            status=Protocolo.Status.EM_ANDAMENTO,
        )

    @patch("atendimentos.chat_services.LLMOrchestrator")
    def test_chat_rag_nao_cria_notificacao(self, mock_orch_cls):
        mock_orch_cls.return_value.processar_turno.return_value = TurnResult(
            resposta_cidadao="Posso ajudar com iluminação ou buracos.",
            acao_ui=None,
        )
        msg_cid = MensagemChat.objects.create(
            sessao=self.sessao,
            autor=MensagemChat.Autor.CIDADAO,
            conteudo_texto="Preciso de ajuda",
        )
        antes = NotificacaoCidadao.objects.filter(usuario=self.cidadao).count()
        executar_processamento_ia(self.sessao, msg_cidadao=msg_cid)
        depois = NotificacaoCidadao.objects.filter(usuario=self.cidadao).count()
        self.assertEqual(antes, depois)

    def test_marco_protocolo_continua_notificando(self):
        antes = NotificacaoCidadao.objects.filter(usuario=self.cidadao).count()
        notificar_status_protocolo(self.protocolo, Protocolo.Status.EM_ANDAMENTO)
        depois = NotificacaoCidadao.objects.filter(usuario=self.cidadao).count()
        self.assertEqual(depois, antes + 1)


class LimparNotificacoesChatRagTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cat = CategoriaCatalogo.objects.create(nome="C", slug="c-limp", ativo=True)
        unidade = UnidadeAdministrativa.objects.create(nome="UA", sigla="UA", ativo=True)
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="S",
            unidade_responsavel=unidade,
            ativo=True,
        )

    def test_queryset_identifica_chat_rag(self):
        cid = User.objects.create_user(
            cpf="11144477735",
            password="x",
            nome="X",
            email="x@test.local",
        )
        NotificacaoCidadao.objects.create(
            usuario=cid,
            titulo="Nova mensagem na conversa",
            mensagem="Assistente M.Ouve: olá",
            protocolo=None,
        )
        proto = Protocolo.objects.create(
            codigo="P-LIMP-1",
            usuario=cid,
            servico=self.servico,
            descricao="d",
            status=Protocolo.Status.EM_ANDAMENTO,
        )
        NotificacaoCidadao.objects.create(
            usuario=cid,
            titulo="Protocolo em andamento",
            mensagem="Sua solicitação P-LIMP-1 está sendo atendida.",
            protocolo=proto,
        )
        self.assertEqual(queryset_notificacoes_chat_rag().count(), 1)


class GovernancaBuscaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.unidade_a = UnidadeAdministrativa.objects.create(
            nome="Secretaria de Saúde",
            sigla="SMS",
            descricao="Atenção básica",
            ativo=True,
        )
        UnidadeAdministrativa.objects.create(
            nome="Obras",
            sigla="OBR",
            descricao="Pavimentação",
            ativo=True,
        )
        cls.perfil = PerfilAcesso.objects.create(
            codigo="super_s45",
            nome="Analista Ouvidoria",
            permissoes=_perms_super(),
            ativo=True,
        )
        cls.admin = User.objects.create_user(
            cpf="12345678909",
            password="x",
            nome="Admin Busca",
            email="admin.busca@test.local",
            is_staff=True,
            perfil_acesso=cls.perfil,
        )
        User.objects.create_user(
            cpf="98765432100",
            password="x",
            nome="João Silva Servidor",
            email="joao.silva@municipio.gov",
            is_staff=True,
            perfil_acesso=cls.perfil,
            unidade=cls.unidade_a,
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_busca_unidades(self):
        resp = self.client.get("/api/v1/backoffice/unidades", {"busca": "saúde"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        nomes = [u["nome"] for u in resp.data]
        self.assertIn("Secretaria de Saúde", nomes)
        self.assertNotIn("Obras", nomes)

    def test_busca_usuarios_por_email(self):
        resp = self.client.get("/api/v1/backoffice/usuarios", {"search": "joao.silva"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        emails = [u.get("email", "") for u in resp.data]
        self.assertTrue(any("joao.silva" in e for e in emails))