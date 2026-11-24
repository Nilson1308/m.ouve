"""Sprint 4 — reabertura, CSAT e KPI retrabalho."""

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from atendimentos.models import (
    AnexoProtocolo,
    AvaliacaoProtocolo,
    ConfiguracaoSlaCobranca,
    OrdemServico,
    Protocolo,
    ReaberturaProtocolo,
)
from atendimentos.services.analytics_service import calcular_kpi_retrabalho, dashboard_qualidade
from atendimentos.services.reabertura_service import (
    aplicar_janela_reabertura_apos_conclusao,
    avaliar_elegibilidade_reabertura,
    encerrar_janelas_reabertura_expiradas,
)
from atendimentos.tasks import encerrar_janelas_reabertura_expiradas_task
from catalogo.models import CategoriaCatalogo, ServicoCatalogo, UnidadeAdministrativa
from core_auth.models import PerfilAcesso
from core_auth.rbac import aplicar_regras_automaticas, permissoes_padrao

User = get_user_model()


def _perfil_mesa():
    base = permissoes_padrao()
    base["mesa_trabalho"] = {"ler": True, "criar": True, "editar": True, "excluir": False}
    return aplicar_regras_automaticas(base)


class ReaberturaBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = CategoriaCatalogo.objects.create(
            nome="Cat Reab", slug="cat-reab", ativo=True
        )
        cls.unidade = UnidadeAdministrativa.objects.create(
            nome="Secretaria Reab", sigla="SR", ativo=True
        )
        cls.cidadao = User.objects.create_user(
            cpf="52998224725",
            password="x",
            nome="Cidadão Reab",
            email="cid-reab@test.local",
        )
        cls.gestor = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Gestor Reab",
            email="gest-reab@test.local",
            is_staff=True,
        )
        perfil = PerfilAcesso.objects.create(
            codigo="gestor_reab",
            nome="Gestor Reab",
            permissoes=_perfil_mesa(),
            ativo=True,
        )
        cls.gestor.perfil_acesso = perfil
        cls.gestor.save()

    def _servico_direto(self, **kwargs):
        data = dict(
            categoria=self.categoria,
            nome="Serviço Direto Reab",
            unidade_responsavel=self.unidade,
            sla_horas=48,
            fluxo_tramitacao=ServicoCatalogo.FluxoTramitacao.DIRETO_SECRETARIA,
            exigir_validacao_ouvidoria=False,
            ativo=True,
        )
        data.update(kwargs)
        return ServicoCatalogo.objects.create(**data)

    def _servico_ouvidoria(self, **kwargs):
        data = dict(
            categoria=self.categoria,
            nome="Serviço Ouvidoria Reab",
            unidade_responsavel=self.unidade,
            sla_horas=72,
            fluxo_tramitacao=ServicoCatalogo.FluxoTramitacao.OUVIDORIA_ENCAMINHA,
            exigir_validacao_ouvidoria=True,
            ativo=True,
        )
        data.update(kwargs)
        return ServicoCatalogo.objects.create(**data)

    def _protocolo(self, servico, *, status=Protocolo.Status.RESOLVIDO):
        return Protocolo.objects.create(
            codigo=Protocolo.gerar_codigo(),
            usuario=self.cidadao,
            servico=servico,
            dados_dinamicos={},
            descricao="Teste reabertura",
            status=status,
            resposta_cidadao="Concluído.",
        )

    def _concluir_com_janela(self, protocolo):
        protocolo.status = Protocolo.Status.RESOLVIDO
        protocolo.save(update_fields=["status", "data_atualizacao"])
        aplicar_janela_reabertura_apos_conclusao(protocolo)
        protocolo.refresh_from_db()


class JanelaReaberturaTests(ReaberturaBase):
    def test_conclusao_popula_reabertura_ate(self):
        cfg = ConfiguracaoSlaCobranca.load()
        cfg.reabertura_ativa = True
        cfg.prazo_reabertura_dias = 5
        cfg.save()
        servico = self._servico_direto()
        p = self._protocolo(servico, status=Protocolo.Status.EM_ANDAMENTO)
        self._concluir_com_janela(p)
        self.assertIsNotNone(p.reabertura_ate)
        self.assertIsNone(p.encerrado_definitivamente_em)

    def test_override_servico_zero_desabilita(self):
        cfg = ConfiguracaoSlaCobranca.load()
        cfg.reabertura_ativa = True
        cfg.save()
        servico = self._servico_direto(prazo_reabertura_dias=0)
        p = self._protocolo(servico)
        self._concluir_com_janela(p)
        self.assertIsNone(p.reabertura_ate)
        eleg = avaliar_elegibilidade_reabertura(p)
        self.assertFalse(eleg.pode)
        self.assertEqual(eleg.motivo, "desabilitado")

    def test_override_servico_dias(self):
        cfg = ConfiguracaoSlaCobranca.load()
        cfg.prazo_reabertura_dias = 7
        cfg.save()
        servico = self._servico_direto(prazo_reabertura_dias=3)
        p = self._protocolo(servico)
        antes = timezone.now()
        self._concluir_com_janela(p)
        delta = p.reabertura_ate - antes
        self.assertGreaterEqual(delta.days, 2)
        self.assertLessEqual(delta.days, 4)


class CsatGatilhoTests(ReaberturaBase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.cidadao)
        cfg = ConfiguracaoSlaCobranca.load()
        cfg.nota_csat_gatilho_reabertura = 2
        cfg.save()
        self.servico = self._servico_direto()
        self.protocolo = self._protocolo(self.servico)
        self._concluir_com_janela(self.protocolo)

    def test_csat_nota_2_sugere_reabertura(self):
        url = f"/api/v1/app/protocolos/{self.protocolo.pk}/avaliar"
        resp = self.client.post(url, {"nota": 2, "comentario": "Ruim"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(resp.data["sugerir_reabertura_csat"])
        self.assertTrue(resp.data["pode_reabrir"])

    def test_csat_nota_5_nao_sugere(self):
        url = f"/api/v1/app/protocolos/{self.protocolo.pk}/avaliar"
        resp = self.client.post(url, {"nota": 5}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertFalse(resp.data["sugerir_reabertura_csat"])


class ReabrirFluxoTests(ReaberturaBase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.cidadao)
        cfg = ConfiguracaoSlaCobranca.load()
        cfg.max_reaberturas_por_protocolo = 1
        cfg.save()

    @patch("atendimentos.notificacoes_internas.notificar_nova_os_unidade")
    @patch("atendimentos.services.reabertura_service.notificar_reabertura_ouvidoria")
    def test_reabrir_direto_secretaria_cria_os(self, _mock_ouv, _mock_os):
        servico = self._servico_direto()
        p = self._protocolo(servico)
        self._concluir_com_janela(p)
        anexo = AnexoProtocolo.objects.create(
            protocolo=p,
            arquivo="protocolos/anexos/2026/11/x.jpg",
            tipo_mime="image/jpeg",
        )
        resp_anexo = self.client.post(
            f"/api/v1/protocolos/{p.pk}/anexos",
            {"fotos": []},
            format="multipart",
        )
        resp = self.client.post(
            f"/api/v1/protocolos/{p.pk}/reabrir",
            {
                "motivo": "Problema não resolvido de fato.",
                "anexos_ids": [str(anexo.id)],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        p.refresh_from_db()
        self.assertEqual(p.status, Protocolo.Status.EM_ANDAMENTO)
        self.assertEqual(p.qtd_reaberturas, 1)
        self.assertIsNone(p.reabertura_ate)
        self.assertTrue(
            ReaberturaProtocolo.objects.filter(protocolo=p).exists()
        )
        self.assertTrue(
            OrdemServico.objects.filter(protocolo=p, reabertura_origem__isnull=False).exists()
        )
        self.assertEqual(len(resp.data["reabertura"]["anexos"]), 1)
        self.assertTrue(resp.data["reabertura"]["anexos"][0]["url"])

    @patch("atendimentos.services.reabertura_service.notificar_reabertura_ouvidoria")
    def test_reabrir_ouvidoria_em_analise(self, _mock):
        servico = self._servico_ouvidoria()
        p = self._protocolo(servico)
        self._concluir_com_janela(p)
        self.client.post(
            f"/api/v1/protocolos/{p.pk}/reabrir",
            {"motivo": "Contestação do cidadão válida."},
            format="json",
        )
        p.refresh_from_db()
        self.assertEqual(p.status, Protocolo.Status.EM_ANALISE)


class BloqueiosReaberturaTests(ReaberturaBase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.cidadao)
        self.servico = self._servico_direto()

    def test_bloqueio_janela_expirada(self):
        p = self._protocolo(self.servico)
        self._concluir_com_janela(p)
        Protocolo.objects.filter(pk=p.pk).update(
            reabertura_ate=timezone.now() - timedelta(days=1)
        )
        resp = self.client.post(
            f"/api/v1/protocolos/{p.pk}/reabrir",
            {"motivo": "Tarde demais para contestar."},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bloqueio_nao_concluido(self):
        p = self._protocolo(self.servico, status=Protocolo.Status.EM_ANDAMENTO)
        resp = self.client.post(
            f"/api/v1/protocolos/{p.pk}/reabrir",
            {"motivo": "Ainda não concluiu o serviço."},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bloqueio_limite_reaberturas(self):
        cfg = ConfiguracaoSlaCobranca.load()
        cfg.max_reaberturas_por_protocolo = 1
        cfg.save()
        p = self._protocolo(self.servico)
        p.qtd_reaberturas = 1
        p.save(update_fields=["qtd_reaberturas"])
        self._concluir_com_janela(p)
        resp = self.client.post(
            f"/api/v1/protocolos/{p.pk}/reabrir",
            {"motivo": "Segunda tentativa bloqueada."},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class CeleryEncerramentoTests(ReaberturaBase):
    def test_task_encerra_janela(self):
        servico = self._servico_direto()
        p = self._protocolo(servico)
        self._concluir_com_janela(p)
        Protocolo.objects.filter(pk=p.pk).update(
            reabertura_ate=timezone.now() - timedelta(hours=2)
        )
        total = encerrar_janelas_reabertura_expiradas()
        self.assertGreaterEqual(total, 1)
        p.refresh_from_db()
        self.assertIsNotNone(p.encerrado_definitivamente_em)

    def test_celery_task_wrapper(self):
        self.test_task_encerra_janela()
        self.assertIsInstance(encerrar_janelas_reabertura_expiradas_task(), int)


class KpiRetrabalhoTests(ReaberturaBase):
    def test_kpi_retrabalho(self):
        s1 = self._servico_direto(nome="S1")
        s2 = self._servico_direto(nome="S2")
        p1 = self._protocolo(s1)
        p2 = self._protocolo(s2)
        p1.qtd_reaberturas = 1
        p1.save(update_fields=["qtd_reaberturas"])
        from atendimentos.models import Protocolo as P

        qs = P.objects.filter(pk__in=[p1.pk, p2.pk])
        kpi = calcular_kpi_retrabalho(qs)
        self.assertEqual(kpi["total_reabertos"], 1)
        self.assertEqual(kpi["taxa_retrabalho_percentual"], 50.0)

    def test_dashboard_qualidade_kpi(self):
        s1 = self._servico_direto()
        p1 = self._protocolo(s1)
        p1.qtd_reaberturas = 1
        p1.save(update_fields=["qtd_reaberturas"])
        data = dashboard_qualidade(self.gestor, {})
        self.assertIn("total_reabertos", data["resumo_geral"])
        self.assertIn("taxa_retrabalho_percentual", data["resumo_geral"])
        self.assertIn("matriz_servicos", data)