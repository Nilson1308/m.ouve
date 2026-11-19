"""CSAT — avaliação PWA, detalhe do protocolo e dashboard qualidade com escopo."""

from django.contrib.auth import get_user_model

from atendimentos.models import AvaliacaoProtocolo, Protocolo
from atendimentos.services.analytics_service import dashboard_qualidade
from atendimentos.services.csat_service import calcular_resumo_csat
from atendimentos.services.escopo_dados import queryset_protocolos_escopo
from catalogo.models import CategoriaCatalogo, ServicoCatalogo, UnidadeAdministrativa
from core_auth.models import PerfilAcesso
from core_auth.rbac import aplicar_regras_automaticas, permissoes_padrao
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


def _perfil_municipio():
    base = permissoes_padrao()
    base["mesa_trabalho"] = {"ler": True, "criar": True, "editar": True, "excluir": False}
    return aplicar_regras_automaticas(base)


def _perfil_unidade():
    base = permissoes_padrao()
    base["mesa_trabalho"] = {"ler": True, "criar": False, "editar": False, "excluir": False}
    return aplicar_regras_automaticas(base, requer_vinculo=True)


class CsatDetalheProtocoloTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cidadao = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Cidadão CSAT detail",
            email="csat.detail@test.local",
        )
        cat = CategoriaCatalogo.objects.create(nome="Cat", slug="cat-csat", ativo=True)
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cat, nome="Serv", ativo=True
        )
        cls.protocolo_aberto = Protocolo.objects.create(
            codigo="PROT-CSAT-AB2",
            usuario=cls.cidadao,
            servico=cls.servico,
            descricao="Aberto",
            status=Protocolo.Status.EM_ANDAMENTO,
        )
        cls.protocolo_ok = Protocolo.objects.create(
            codigo="PROT-CSAT-OK2",
            usuario=cls.cidadao,
            servico=cls.servico,
            descricao="Resolvido",
            status=Protocolo.Status.RESOLVIDO,
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.cidadao)

    def test_detalhe_pode_avaliar_quando_resolvido_sem_nota(self):
        resp = self.client.get(f"/api/v1/protocolos/{self.protocolo_ok.codigo}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["pode_avaliar"])
        self.assertIsNone(resp.data["avaliacao"])

    def test_detalhe_nao_pode_avaliar_em_andamento(self):
        resp = self.client.get(f"/api/v1/protocolos/{self.protocolo_aberto.codigo}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(resp.data["pode_avaliar"])
        self.assertIsNone(resp.data["avaliacao"])


class CsatAnalyticsEscopoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cidadao = User.objects.create_user(
            cpf="15350946056",
            password="x",
            nome="Cidadão",
            email="c@test.local",
        )
        cls.unidade_a = UnidadeAdministrativa.objects.create(
            nome="UA CSAT", sigla="UCS", ativo=True
        )
        cls.unidade_b = UnidadeAdministrativa.objects.create(
            nome="UB CSAT", sigla="UBS", ativo=True
        )
        cat = CategoriaCatalogo.objects.create(nome="Cat", slug="cat-an", ativo=True)
        cls.servico_a = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="SA",
            unidade_responsavel=cls.unidade_a,
            ativo=True,
        )
        cls.servico_b = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="SB",
            unidade_responsavel=cls.unidade_b,
            ativo=True,
        )
        cls.perfil = PerfilAcesso.objects.create(
            codigo="gest_csat_escopo",
            nome="Gestor CSAT",
            permissoes=_perfil_unidade(),
            ativo=True,
        )
        cls.gestor_a = User.objects.create_user(
            cpf="52998224725",
            password="x",
            nome="Gestor A",
            email="ga@test.local",
            perfil_acesso=cls.perfil,
            unidade=cls.unidade_a,
            is_staff=True,
        )
        cls.ouvidor = User.objects.create_user(
            cpf="11144477735",
            password="x",
            nome="Ouvidor",
            email="ouv@test.local",
            perfil_acesso=PerfilAcesso.objects.create(
                codigo="ouv_csat",
                nome="Ouv",
                permissoes=_perfil_municipio(),
                ativo=True,
            ),
            is_staff=True,
        )

        for codigo, servico, nota in (
            ("PROT-CSA-5", cls.servico_a, 5),
            ("PROT-CSA-3", cls.servico_a, 3),
            ("PROT-CSB-5", cls.servico_b, 5),
        ):
            p = Protocolo.objects.create(
                codigo=codigo,
                usuario=cls.cidadao,
                servico=servico,
                descricao="Teste CSAT",
                status=Protocolo.Status.RESOLVIDO,
            )
            AvaliacaoProtocolo.objects.create(protocolo=p, nota=nota, comentario="")

    def test_gestor_a_ve_media_apenas_unidade_a(self):
        qs = queryset_protocolos_escopo(self.gestor_a)
        resumo = calcular_resumo_csat(qs)
        self.assertEqual(resumo["total_avaliacoes"], 2)
        self.assertEqual(resumo["media_satisfacao"], 4.0)
        self.assertEqual(resumo["percentual_satisfeitos"], 50.0)

    def test_dashboard_qualidade_resumo_respeita_escopo(self):
        data = dashboard_qualidade(self.gestor_a, {})
        resumo = data["resumo_geral"]
        self.assertEqual(resumo["total_avaliacoes"], 2)
        self.assertEqual(resumo["media_satisfacao"], 4.0)
        self.assertEqual(data["escopo"], "unidade")

    def test_ouvidor_ve_csat_municipio(self):
        qs = queryset_protocolos_escopo(self.ouvidor)
        resumo = calcular_resumo_csat(qs)
        self.assertEqual(resumo["total_avaliacoes"], 3)
        self.assertAlmostEqual(resumo["media_satisfacao"], 4.3, places=1)