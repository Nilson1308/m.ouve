"""Sprint 3 — diligência, pausa de SLA e expiração."""

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from atendimentos.models import (
    ConfiguracaoSlaCobranca,
    DiligenciaProtocolo,
    OrdemServico,
    Protocolo,
)
from atendimentos.services.diligencia_service import abrir_diligencia, diligencia_aguardando
from atendimentos.services.sla_cobranca_service import (
    avaliar_elegibilidade_cobranca,
    queryset_protocolos_atrasados,
    sla_vencido,
)
from atendimentos.tasks import verificar_expiracao_diligencias_task
from catalogo.models import CategoriaCatalogo, ServicoCatalogo, UnidadeAdministrativa
from core_auth.models import PerfilAcesso
from core_auth.rbac import aplicar_regras_automaticas, permissoes_padrao

User = get_user_model()


def _perfil_mesa():
    base = permissoes_padrao()
    base["mesa_trabalho"] = {"ler": True, "criar": True, "editar": True, "excluir": False}
    return aplicar_regras_automaticas(base)


class DiligenciaBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = CategoriaCatalogo.objects.create(
            nome="Cat Dilig", slug="cat-dilig", ativo=True
        )
        cls.unidade = UnidadeAdministrativa.objects.create(
            nome="Secretaria Dilig", sigla="SD", ativo=True
        )
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Serviço Dilig",
            unidade_responsavel=cls.unidade,
            sla_horas=48,
            ativo=True,
        )
        cls.cidadao = User.objects.create_user(
            cpf="39053344706",
            password="x",
            nome="Cidadão Dilig",
            email="cid-dilig@test.local",
        )
        cls.servidor = User.objects.create_user(
            cpf="52998224726",
            password="x",
            nome="Servidor Dilig",
            email="srv-dilig@test.local",
            is_staff=True,
            unidade=cls.unidade,
        )
        perfil = PerfilAcesso.objects.create(
            codigo="gestor_dilig",
            nome="Gestor Dilig",
            permissoes=_perfil_mesa(),
            ativo=True,
        )
        cls.servidor.perfil_acesso = perfil
        cls.servidor.save()

    def _protocolo(self, *, horas_atras=60, status=Protocolo.Status.EM_ANDAMENTO):
        p = Protocolo.objects.create(
            codigo=Protocolo.gerar_codigo(),
            usuario=self.cidadao,
            servico=self.servico,
            dados_dinamicos={},
            descricao="Teste diligência",
            status=status,
        )
        Protocolo.objects.filter(pk=p.pk).update(
            data_criacao=timezone.now() - timedelta(hours=horas_atras)
        )
        p.refresh_from_db()
        return p


class AbrirDiligenciaTests(DiligenciaBase):
    @patch("atendimentos.services.diligencia_service.criar_notificacao_cidadao")
    def test_abrir_pausa_sla_e_bloqueia_segunda(self, mock_notif):
        cfg = ConfiguracaoSlaCobranca.load()
        cfg.diligencia_ativa = True
        cfg.max_diligencias_por_protocolo = 2
        cfg.prazo_diligencia_dias = 5
        cfg.save()

        p = self._protocolo()
        self.assertTrue(sla_vencido(p))

        d1 = abrir_diligencia(
            p,
            autor=self.servidor,
            unidade_solicitante_id=self.unidade.pk,
            pergunta="Envie foto do local.",
        )
        p.refresh_from_db()
        self.assertEqual(p.status, Protocolo.Status.AGUARDANDO_CIDADAO)
        self.assertIsNotNone(p.sla_pausado_desde)
        self.assertFalse(sla_vencido(p))
        mock_notif.assert_called_once()

        with self.assertRaises(ValidationError):
            abrir_diligencia(
                p,
                autor=self.servidor,
                unidade_solicitante_id=self.unidade.pk,
                pergunta="Outra pergunta",
            )

        self.assertEqual(d1.status, DiligenciaProtocolo.Status.AGUARDANDO_CIDADAO)


class SlaCobrancaPausaTests(DiligenciaBase):
    def test_excluido_sla_atrasados_e_cobranca_bloqueada(self):
        p = self._protocolo()
        abrir_diligencia(
            p,
            autor=self.servidor,
            unidade_solicitante_id=self.unidade.pk,
            pergunta="Preciso do CPF completo.",
        )
        p.refresh_from_db()
        self.assertFalse(sla_vencido(p))
        ids = list(queryset_protocolos_atrasados().values_list("pk", flat=True))
        self.assertNotIn(p.pk, ids)

        eleg = avaliar_elegibilidade_cobranca(p, self.cidadao)
        self.assertFalse(eleg.pode)
        self.assertEqual(eleg.motivo, "aguardando_cidadao")


class ResponderDiligenciaTests(DiligenciaBase):
    def test_resposta_prorroga_prazo_sla(self):
        from atendimentos.models import AnexoProtocolo
        from atendimentos.services.diligencia_service import responder_diligencia

        p = self._protocolo(horas_atras=50)
        antes_prazo = p.data_criacao + timedelta(hours=48)
        abrir_diligencia(
            p,
            autor=self.servidor,
            unidade_solicitante_id=self.unidade.pk,
            pergunta="Anexe o comprovante.",
            exige_anexo=True,
        )
        p.refresh_from_db()
        pausa_inicio = timezone.now() - timedelta(hours=2)
        Protocolo.objects.filter(pk=p.pk).update(sla_pausado_desde=pausa_inicio)
        p.refresh_from_db()
        self.assertIsNotNone(p.sla_pausado_desde)

        d = diligencia_aguardando(p)
        anexo = AnexoProtocolo.objects.create(protocolo=p, tipo_mime="image/jpeg")

        with patch(
            "atendimentos.services.diligencia_service._notificar_unidade_resposta"
        ):
            responder_diligencia(
                p,
                d.id,
                resposta="Segue comprovante em anexo.",
                anexos_ids=[str(anexo.id)],
            )

        p.refresh_from_db()
        self.assertIsNone(p.sla_pausado_desde)
        self.assertGreater(p.tempo_sla_pausado_segundos, 0)
        self.assertIsNotNone(p.prazo_sla)
        self.assertGreater(p.prazo_sla, antes_prazo)
        self.assertEqual(p.status, Protocolo.Status.EM_ANDAMENTO)


class LimiteDiligenciasTests(DiligenciaBase):
    def test_limite_max_diligencias(self):
        cfg = ConfiguracaoSlaCobranca.load()
        cfg.max_diligencias_por_protocolo = 1
        cfg.save()

        p = self._protocolo()
        with patch("atendimentos.services.diligencia_service.criar_notificacao_cidadao"):
            d = abrir_diligencia(
                p,
                autor=self.servidor,
                unidade_solicitante_id=self.unidade.pk,
                pergunta="Pergunta 1",
            )
            d.status = DiligenciaProtocolo.Status.RESPONDIDA
            d.save()
            p.refresh_from_db()
            p.status = Protocolo.Status.EM_ANDAMENTO
            p.sla_pausado_desde = None
            p.save()

        with self.assertRaises(ValidationError):
            abrir_diligencia(
                p,
                autor=self.servidor,
                unidade_solicitante_id=self.unidade.pk,
                pergunta="Pergunta 2",
            )


class ExpiracaoDiligenciaTests(DiligenciaBase):
    @patch("atendimentos.services.diligencia_service.criar_notificacao_cidadao")
    def test_expiracao_devolver_fila(self, _mock):
        cfg = ConfiguracaoSlaCobranca.load()
        cfg.acao_expiracao_diligencia = "devolver_fila"
        cfg.save()

        p = self._protocolo()
        with patch("atendimentos.services.diligencia_service.criar_notificacao_cidadao"):
            abrir_diligencia(
                p,
                autor=self.servidor,
                unidade_solicitante_id=self.unidade.pk,
                pergunta="Responda até amanhã.",
            )
        d = diligencia_aguardando(p)
        DiligenciaProtocolo.objects.filter(pk=d.pk).update(
            prazo_resposta=timezone.now() - timedelta(hours=1)
        )

        with patch("atendimentos.services.diligencia_service.criar_notificacao_interna"):
            n = verificar_expiracao_diligencias_task()
        self.assertGreaterEqual(n, 1)
        p.refresh_from_db()
        d.refresh_from_db()
        self.assertEqual(d.status, DiligenciaProtocolo.Status.EXPIRADA)
        self.assertEqual(p.status, Protocolo.Status.EM_ANDAMENTO)

    @patch("atendimentos.services.diligencia_service.criar_notificacao_cidadao")
    def test_expiracao_encerrar_sem_resposta(self, mock_cid):
        cfg = ConfiguracaoSlaCobranca.load()
        cfg.acao_expiracao_diligencia = "encerrar_sem_resposta"
        cfg.save()

        p = self._protocolo()
        with patch("atendimentos.services.diligencia_service.criar_notificacao_cidadao"):
            abrir_diligencia(
                p,
                autor=self.servidor,
                unidade_solicitante_id=self.unidade.pk,
                pergunta="Urgente.",
            )
        d = diligencia_aguardando(p)
        DiligenciaProtocolo.objects.filter(pk=d.pk).update(
            prazo_resposta=timezone.now() - timedelta(minutes=5)
        )

        with patch("atendimentos.services.diligencia_service.criar_notificacao_interna"):
            verificar_expiracao_diligencias_task()
        p.refresh_from_db()
        self.assertEqual(p.status, Protocolo.Status.REJEITADO)


class ApiResponderDiligenciaTests(DiligenciaBase):
    @patch("atendimentos.services.diligencia_service.criar_notificacao_cidadao")
    def test_post_responder_diligencia_pwa(self, _mock):
        p = self._protocolo()
        abrir_diligencia(
            p,
            autor=self.servidor,
            unidade_solicitante_id=self.unidade.pk,
            pergunta="Qual o número do imóvel?",
        )
        client = APIClient()
        client.force_authenticate(user=self.cidadao)
        with patch(
            "atendimentos.services.diligencia_service._notificar_unidade_resposta"
        ):
            resp = client.post(
                f"/api/v1/protocolos/{p.codigo}/responder-diligencia",
                {"resposta": "Número 123"},
                format="json",
            )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        p.refresh_from_db()
        self.assertEqual(p.status, Protocolo.Status.EM_ANDAMENTO)