"""Sprint 2.5 — governança real de fluxos (direto vs ouvidoria)."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from atendimentos.backoffice_services import (
    concluir_atendimento_setor,
    marcar_ordem_concluida,
)
from atendimentos.models import OrdemServico, Protocolo, ProtocoloHistorico
from atendimentos.services.fluxo_governanca_service import (
    processar_governanca_entrada_protocolo,
)
from atendimentos.services.triagem_service import (
    FONTE_CATALOGO_EXECUTOR,
    FONTE_EQUIPAMENTO,
    executar_triagem_protocolo,
)
from catalogo.models import (
    CategoriaCatalogo,
    EquipamentoPublico,
    ServicoCatalogo,
    UnidadeAdministrativa,
)
User = get_user_model()


class FluxoGovernancaMigrationTests(TestCase):
    def test_hibrido_rejeitado_no_serializer(self):
        from catalogo.governanca_serializers import ServicoCatalogoGovernancaSerializer

        cat = CategoriaCatalogo.objects.create(nome="Cat Gov", slug="cat-gov", ativo=True)
        unidade = UnidadeAdministrativa.objects.create(nome="U", sigla="U", ativo=True)
        ser = ServicoCatalogoGovernancaSerializer(
            data={
                "nome": "Serv hibrido",
                "categoria_id": str(cat.id),
                "unidade_responsavel_id": str(unidade.id),
                "fluxo_tramitacao": "hibrido",
            }
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("hibrido", str(ser.errors).lower())


class DiretoSecretariaEntradaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            cpf="39053344708",
            password="x",
            nome="Cid",
            email="direto@test.local",
        )
        cls.exec = UnidadeAdministrativa.objects.create(
            nome="Secretaria Exec", sigla="SEX", ativo=True
        )
        cls.cat = CategoriaCatalogo.objects.create(nome="Zel", slug="zel-gov", ativo=True)
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cls.cat,
            nome="Serviço direto",
            fluxo_tramitacao=ServicoCatalogo.FluxoTramitacao.DIRETO_SECRETARIA,
            unidade_responsavel=cls.exec,
            exigir_validacao_ouvidoria=False,
            ativo=True,
            sla_horas=48,
        )

    @patch("atendimentos.notificacoes_cidadao.notificar_status_protocolo")
    @patch("atendimentos.notificacoes_internas.notificar_despacho_scatter")
    def test_api_cria_os_automatica(self, mock_scatter, mock_cidadao):
        mock_scatter.return_value = 1
        protocolo = Protocolo.objects.create(
            codigo="PROT-DIR-API",
            usuario=self.user,
            servico=self.servico,
            descricao="Teste auto",
        )
        executar_triagem_protocolo(protocolo)
        processar_governanca_entrada_protocolo(protocolo)
        protocolo.refresh_from_db()
        self.assertEqual(protocolo.status, Protocolo.Status.EM_ANDAMENTO)
        os_qs = OrdemServico.objects.filter(protocolo=protocolo)
        self.assertEqual(os_qs.count(), 1)
        self.assertEqual(os_qs.first().unidade_id, self.exec.id)
        mock_scatter.assert_called_once()
        hist = ProtocoloHistorico.objects.filter(protocolo=protocolo).values_list(
            "descricao", flat=True
        )
        self.assertTrue(any("Despacho automático" in h for h in hist))

    def test_idempotencia_dois_despachos(self):
        protocolo = Protocolo.objects.create(
            codigo="PROT-DIR-IDEM",
            usuario=self.user,
            servico=self.servico,
            descricao="Idem",
        )
        processar_governanca_entrada_protocolo(protocolo)
        processar_governanca_entrada_protocolo(protocolo)
        self.assertEqual(OrdemServico.objects.filter(protocolo=protocolo).count(), 1)

    def test_fallback_unidade_inativa(self):
        inativa = UnidadeAdministrativa.objects.create(
            nome="Inativa", sigla="INA", ativo=False
        )
        servico = ServicoCatalogo.objects.create(
            categoria=self.cat,
            nome="Sem unidade ativa",
            fluxo_tramitacao=ServicoCatalogo.FluxoTramitacao.DIRETO_SECRETARIA,
            unidade_responsavel=inativa,
            exigir_validacao_ouvidoria=False,
            ativo=True,
        )
        protocolo = Protocolo.objects.create(
            codigo="PROT-FALL",
            usuario=self.user,
            servico=servico,
            descricao="Fallback",
        )
        processar_governanca_entrada_protocolo(protocolo)
        protocolo.refresh_from_db()
        self.assertEqual(protocolo.status, Protocolo.Status.EM_ANALISE)
        self.assertFalse(OrdemServico.objects.filter(protocolo=protocolo).exists())


class DiretoSecretariaSaidaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            cpf="39053344709",
            password="x",
            nome="Cid2",
            email="saida@test.local",
        )
        cls.exec = UnidadeAdministrativa.objects.create(
            nome="Exec2", sigla="EX2", ativo=True
        )
        cat = CategoriaCatalogo.objects.create(nome="C2", slug="c2", ativo=True)
        cls.servico_sem_val = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Direto sem val",
            fluxo_tramitacao=ServicoCatalogo.FluxoTramitacao.DIRETO_SECRETARIA,
            unidade_responsavel=cls.exec,
            exigir_validacao_ouvidoria=False,
            ativo=True,
        )
        cls.servico_com_val = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Direto com val",
            fluxo_tramitacao=ServicoCatalogo.FluxoTramitacao.DIRETO_SECRETARIA,
            unidade_responsavel=cls.exec,
            exigir_validacao_ouvidoria=True,
            ativo=True,
        )

    @patch("atendimentos.notificacoes_cidadao.notificar_status_protocolo")
    def test_conclusao_encerra_protocolo_sem_validacao(self, mock_notif):
        protocolo = Protocolo.objects.create(
            codigo="PROT-RES-DIR",
            usuario=self.user,
            servico=self.servico_sem_val,
            descricao="x",
            status=Protocolo.Status.EM_ANDAMENTO,
        )
        ordem = OrdemServico.objects.create(
            protocolo=protocolo,
            unidade=self.exec,
            descricao="OS",
            status=OrdemServico.Status.EM_ANDAMENTO,
        )
        marcar_ordem_concluida(ordem, despacho_tecnico="Problema resolvido no poste.")
        ok = concluir_atendimento_setor(
            protocolo,
            ordem,
            despacho_tecnico="Problema resolvido no poste.",
            unidade_nome="EX2",
        )
        protocolo.refresh_from_db()
        self.assertTrue(ok)
        self.assertEqual(protocolo.status, Protocolo.Status.RESOLVIDO)
        self.assertIn("poste", protocolo.resposta_cidadao.lower())
        mock_notif.assert_called()

    @patch("atendimentos.notificacoes_cidadao.notificar_status_protocolo")
    def test_conclusao_com_validacao_vai_revisao(self, mock_notif):
        protocolo = Protocolo.objects.create(
            codigo="PROT-REV",
            usuario=self.user,
            servico=self.servico_com_val,
            descricao="x",
            status=Protocolo.Status.EM_ANDAMENTO,
        )
        ordem = OrdemServico.objects.create(
            protocolo=protocolo,
            unidade=self.exec,
            descricao="OS",
            status=OrdemServico.Status.EM_ANDAMENTO,
        )
        marcar_ordem_concluida(ordem, despacho_tecnico="Feito.")
        ok = concluir_atendimento_setor(
            protocolo, ordem, despacho_tecnico="Feito.", unidade_nome="EX2"
        )
        protocolo.refresh_from_db()
        self.assertTrue(ok)
        self.assertEqual(protocolo.status, Protocolo.Status.AGUARDANDO_REVISAO)
        self.assertNotEqual(protocolo.status, Protocolo.Status.RESOLVIDO)


class OuvidoriaExecutorPadraoTriagemTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            cpf="39053344710",
            password="x",
            nome="C3",
            email="tri@test.local",
        )
        cls.canal = UnidadeAdministrativa.objects.create(
            nome="Ouvidoria", sigla="OUV", ativo=True
        )
        cls.exec = UnidadeAdministrativa.objects.create(
            nome="SMSUZ", sigla="SMSUZ", ativo=True
        )
        cat = CategoriaCatalogo.objects.create(nome="Cat T", slug="cat-t", ativo=True)
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Ouv com executor",
            fluxo_tramitacao=ServicoCatalogo.FluxoTramitacao.OUVIDORIA_ENCAMINHA,
            unidade_responsavel=cls.canal,
            executor_padrao=cls.exec,
            exigir_validacao_ouvidoria=True,
            ativo=True,
        )
        cls.eq = EquipamentoPublico.objects.create(
            nome="Poste 1",
            tipo="outro",
            unidade_responsavel=cls.exec,
            ativo=True,
        )

    def test_triagem_executor_padrao(self):
        p = Protocolo.objects.create(
            codigo="PROT-TRI",
            usuario=self.user,
            servico=self.servico,
            descricao="tri",
            status=Protocolo.Status.EM_ANALISE,
        )
        payload = executar_triagem_protocolo(p)
        fontes = [u["fonte"] for u in payload["unidades_sugeridas"]]
        self.assertIn(FONTE_CATALOGO_EXECUTOR, fontes)
        por_fonte = {u["fonte"]: u for u in payload["unidades_sugeridas"]}
        self.assertEqual(por_fonte[FONTE_CATALOGO_EXECUTOR]["confianca"], 0.95)

    def test_equipamento_prioriza_sobre_executor_padrao(self):
        p = Protocolo.objects.create(
            codigo="PROT-EQ",
            usuario=self.user,
            servico=self.servico,
            descricao="eq",
            equipamento=self.eq,
        )
        payload = executar_triagem_protocolo(p)
        top = payload["unidades_sugeridas"][0]
        self.assertEqual(top["fonte"], FONTE_EQUIPAMENTO)
        self.assertEqual(top["confianca"], 1.0)

    def test_sem_os_na_abertura(self):
        p = Protocolo.objects.create(
            codigo="PROT-ANA",
            usuario=self.user,
            servico=self.servico,
            descricao="ana",
        )
        executar_triagem_protocolo(p)
        processar_governanca_entrada_protocolo(p)
        self.assertEqual(p.status, Protocolo.Status.EM_ANALISE)
        self.assertFalse(OrdemServico.objects.filter(protocolo=p).exists())


class OuvidoriaForcaValidacaoTests(TestCase):
    def test_patch_forca_exigir_validacao(self):
        cat = CategoriaCatalogo.objects.create(nome="C", slug="c-f", ativo=True)
        ouv = UnidadeAdministrativa.objects.create(nome="Ouv", sigla="O", ativo=True)
        exec_u = UnidadeAdministrativa.objects.create(nome="E", sigla="E", ativo=True)
        servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Ouv serv",
            fluxo_tramitacao=ServicoCatalogo.FluxoTramitacao.OUVIDORIA_ENCAMINHA,
            unidade_responsavel=ouv,
            executor_padrao=exec_u,
            ativo=True,
        )
        self.assertTrue(servico.exigir_validacao_ouvidoria)