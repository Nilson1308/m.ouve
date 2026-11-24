"""Sprint 2 — SLA, cobrança do cidadão e relatórios."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from atendimentos.models import CobrancaProtocolo, ConfiguracaoSlaCobranca, Protocolo, ProtocoloHistorico
from atendimentos.services.sla_cobranca_service import (
    NIVEL_ESCALONADO,
    NIVEL_PREVENTIVO,
    NIVEL_VENCIDO,
    avaliar_elegibilidade_cobranca,
    executar_cobranca_cidadao,
    verificar_escalonamento_sla,
)
from catalogo.models import CategoriaCatalogo, ServicoCatalogo, UnidadeAdministrativa
from core_auth.models import PerfilAcesso
from core_auth.rbac import aplicar_regras_automaticas, permissoes_padrao

User = get_user_model()


def _perfil_mesa_staff():
    base = permissoes_padrao()
    base["mesa_trabalho"] = {"ler": True, "criar": True, "editar": True, "excluir": False}
    return aplicar_regras_automaticas(base)


class SlaCobrancaBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = CategoriaCatalogo.objects.create(
            nome="Cat SLA", slug="cat-sla", ativo=True
        )
        cls.unidade = UnidadeAdministrativa.objects.create(
            nome="Secretaria Teste", sigla="ST", ativo=True
        )
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Serviço SLA",
            unidade_responsavel=cls.unidade,
            sla_horas=1,
            ativo=True,
        )
        cls.cidadao = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Cidadão",
            email="cid@test.local",
        )
        cls.gestor = User.objects.create_user(
            cpf="52998224725",
            password="x",
            nome="Gestor",
            email="gestor@test.local",
            is_staff=True,
        )


class CobrancaCidadaoTests(SlaCobrancaBase):
    def _protocolo(self, *, status=Protocolo.Status.EM_ANALISE, horas_atras=0):
        p = Protocolo.objects.create(
            codigo=Protocolo.gerar_codigo(),
            usuario=self.cidadao,
            servico=self.servico,
            dados_dinamicos={},
            descricao="Teste SLA",
            status=status,
        )
        if horas_atras:
            Protocolo.objects.filter(pk=p.pk).update(
                data_criacao=timezone.now() - timedelta(hours=horas_atras)
            )
            p.refresh_from_db()
        return p

    def test_bloqueio_dentro_do_prazo(self):
        p = self._protocolo(horas_atras=0)
        eleg = avaliar_elegibilidade_cobranca(p, self.cidadao)
        self.assertFalse(eleg.pode)
        self.assertEqual(eleg.motivo, "dentro_do_prazo")

    def test_bloqueio_encerrado(self):
        p = self._protocolo(status=Protocolo.Status.RESOLVIDO, horas_atras=5)
        eleg = avaliar_elegibilidade_cobranca(p, self.cidadao)
        self.assertFalse(eleg.pode)
        self.assertEqual(eleg.motivo, "encerrado")

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_cobranca_valida_e_cooldown(self):
        cfg = ConfiguracaoSlaCobranca.load()
        cfg.cooldown_cobranca_horas = 48
        cfg.save()
        p = self._protocolo(horas_atras=3)
        cache.clear()
        cob = executar_cobranca_cidadao(p, self.cidadao, mensagem="Preciso de retorno")
        p.refresh_from_db()
        self.assertEqual(p.qtd_cobrancas_cidadao, 1)
        self.assertIsNotNone(p.ultima_cobranca_em)
        self.assertTrue(ProtocoloHistorico.objects.filter(protocolo=p).exists())
        self.assertTrue(CobrancaProtocolo.objects.filter(pk=cob.pk).exists())

        eleg = avaliar_elegibilidade_cobranca(p, self.cidadao)
        self.assertFalse(eleg.pode)
        self.assertEqual(eleg.motivo, "em_cooldown")

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_api_cobrar_429_no_cooldown(self):
        cfg = ConfiguracaoSlaCobranca.load()
        cfg.cooldown_cobranca_horas = 48
        cfg.save()
        p = self._protocolo(horas_atras=4)
        client = APIClient()
        client.force_authenticate(user=self.cidadao)
        url = f"/api/v1/protocolos/{p.codigo}/cobrar"
        r1 = client.post(url, {"mensagem": "Urgente"}, format="json")
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)
        r2 = client.post(url, {}, format="json")
        self.assertEqual(r2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class EscalonamentoSlaTests(SlaCobrancaBase):
    def test_regua_sem_duplicar_alertas(self):
        cfg = ConfiguracaoSlaCobranca.load()
        cfg.alerta_preventivo_percentual = 50
        cfg.escalonamento_controladoria_dias = 0
        cfg.emails_controladoria = ["controladoria@test.local"]
        cfg.save()

        p = Protocolo.objects.create(
            codigo=Protocolo.gerar_codigo(),
            usuario=self.cidadao,
            servico=self.servico,
            dados_dinamicos={},
            descricao="Atrasado",
            status=Protocolo.Status.EM_ANALISE,
        )
        Protocolo.objects.filter(pk=p.pk).update(
            data_criacao=timezone.now() - timedelta(hours=5)
        )
        p.refresh_from_db()

        n1 = verificar_escalonamento_sla()
        p.refresh_from_db()
        self.assertGreaterEqual(n1, 1)
        nivel1 = p.ultimo_alerta_sla_nivel
        hist1 = ProtocoloHistorico.objects.filter(protocolo=p).count()

        n2 = verificar_escalonamento_sla()
        p.refresh_from_db()
        self.assertEqual(p.ultimo_alerta_sla_nivel, nivel1)
        self.assertEqual(ProtocoloHistorico.objects.filter(protocolo=p).count(), hist1)
        self.assertEqual(n2, 0)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class DigestSlaTests(SlaCobrancaBase):
    def test_digest_agrupado_por_unidade(self):
        from atendimentos.models import RelatorioSlaEnvio
        from atendimentos.services.sla_cobranca_service import enviar_digest_sla_atrasados

        cfg = ConfiguracaoSlaCobranca.load()
        cfg.emails_controladoria = ["ctrl@test.local"]
        cfg.save()

        p = Protocolo.objects.create(
            codigo=Protocolo.gerar_codigo(),
            usuario=self.cidadao,
            servico=self.servico,
            dados_dinamicos={},
            descricao="Vencido",
            status=Protocolo.Status.EM_ANALISE,
            qtd_cobrancas_cidadao=1,
        )
        Protocolo.objects.filter(pk=p.pk).update(
            data_criacao=timezone.now() - timedelta(hours=10)
        )

        mail.outbox.clear()
        envios = enviar_digest_sla_atrasados(incluir_controladoria=True)
        self.assertTrue(envios)
        self.assertTrue(RelatorioSlaEnvio.objects.exists())
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertLessEqual(len(mail.outbox), 3)


class RelatorioApiTests(SlaCobrancaBase):
    def test_export_csv(self):
        perfil = PerfilAcesso.objects.create(
            codigo="gestor_teste_sla",
            nome="Gestor Teste SLA",
            permissoes=_perfil_mesa_staff(),
            ativo=True,
        )
        self.gestor.perfil_acesso = perfil
        self.gestor.save()

        p = Protocolo.objects.create(
            codigo=Protocolo.gerar_codigo(),
            usuario=self.cidadao,
            servico=self.servico,
            dados_dinamicos={},
            descricao="CSV",
            status=Protocolo.Status.EM_ANALISE,
            qtd_cobrancas_cidadao=2,
        )
        Protocolo.objects.filter(pk=p.pk).update(
            data_criacao=timezone.now() - timedelta(hours=8)
        )

        client = APIClient()
        client.force_authenticate(user=self.gestor)
        r = client.get(
            "/api/v1/backoffice/relatorios/sla-atrasados/exportar?apenas_cobrados=true"
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/csv", r["Content-Type"])
        self.assertTrue(r.content.startswith(b"\xef\xbb\xbf"))