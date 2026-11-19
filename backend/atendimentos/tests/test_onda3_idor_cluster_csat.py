"""Onda 3 — IDOR backoffice, cluster por serviço e CSAT (PWA)."""

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from atendimentos.backoffice_services import get_protocolo_backoffice
from atendimentos.cluster_services import (
    clusterizar_por_servico_e_raio,
    gerar_sugestoes_super_os,
    queryset_candidatos_cluster,
)
from catalogo.template_service import duplicar_servico_catalogo
from atendimentos.models import AvaliacaoProtocolo, OrdemServico, Protocolo
from catalogo.models import CategoriaCatalogo, ServicoCatalogo, UnidadeAdministrativa
from core_auth.models import PerfilAcesso
from core_auth.rbac import aplicar_regras_automaticas, permissoes_padrao

User = get_user_model()


def _perfil_mesa_staff():
    base = permissoes_padrao()
    base["mesa_trabalho"] = {"ler": True, "criar": True, "editar": True, "excluir": False}
    return aplicar_regras_automaticas(base)


def _perfil_unidade_staff():
    base = permissoes_padrao()
    base["mesa_trabalho"] = {"ler": True, "criar": True, "editar": False, "excluir": False}
    return aplicar_regras_automaticas(base, requer_vinculo=True)


class BackofficeIdorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cidadao = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Cidadão IDOR",
            email="cidadao.idor@test.local",
        )
        cls.unidade_a = UnidadeAdministrativa.objects.create(nome="UA", sigla="UA", ativo=True)
        cls.unidade_b = UnidadeAdministrativa.objects.create(nome="UB", sigla="UB", ativo=True)
        cls.categoria = CategoriaCatalogo.objects.create(
            nome="Cat IDOR", slug="cat-idor", ativo=True
        )
        cls.servico_b = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Serv B",
            unidade_responsavel=cls.unidade_b,
            ativo=True,
        )
        cls.protocolo_b = Protocolo.objects.create(
            codigo="PROT-IDOR-B",
            usuario=cls.cidadao,
            servico=cls.servico_b,
            descricao="Somente unidade B",
            status=Protocolo.Status.EM_ANALISE,
        )
        cls.perfil_ouvidor = PerfilAcesso.objects.create(
            codigo="teste_ouvidor_idor",
            nome="Ouvidor IDOR",
            permissoes=_perfil_mesa_staff(),
            ativo=True,
        )
        cls.perfil_setor = PerfilAcesso.objects.create(
            codigo="teste_setor_idor",
            nome="Setor A IDOR",
            permissoes=_perfil_unidade_staff(),
            ativo=True,
        )
        cls.ouvidor = User.objects.create_user(
            cpf="15350946056",
            password="x",
            nome="Ouvidor",
            email="ouvidor.idor@test.local",
            perfil_acesso=cls.perfil_ouvidor,
            is_staff=True,
        )
        cls.operador_a = User.objects.create_user(
            cpf="52998224725",
            password="x",
            nome="Operador A",
            email="operador.idor@test.local",
            perfil_acesso=cls.perfil_setor,
            unidade=cls.unidade_a,
            is_staff=True,
        )

    def setUp(self):
        self.client = APIClient()

    def test_get_protocolo_backoffice_bloqueia_outra_unidade(self):
        from django.http import Http404

        with self.assertRaises(Http404):
            get_protocolo_backoffice(self.protocolo_b.pk, user=self.operador_a)

    def test_api_detalhe_protocolo_retorna_404_fora_escopo(self):
        self.client.force_authenticate(user=self.operador_a)
        resp = self.client.get(f"/api/v1/backoffice/protocolos/{self.protocolo_b.pk}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_ouvidor_acessa_protocolo_qualquer_unidade(self):
        self.client.force_authenticate(user=self.ouvidor)
        resp = self.client.get(f"/api/v1/backoffice/protocolos/{self.protocolo_b.pk}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class ClusterPermiteServicoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cidadao = User.objects.create_user(
            cpf="11144477735",
            password="x",
            nome="Cidadão cluster",
            email="cid.cluster@test.local",
        )
        cls.categoria = CategoriaCatalogo.objects.create(
            nome="Cat cluster", slug="cat-cluster", ativo=True
        )
        cls.servico_cluster = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Zeladoria",
            permite_cluster=True,
            ativo=True,
        )
        cls.servico_individual = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Assistência social",
            permite_cluster=False,
            ativo=True,
        )
        ponto = Point(-46.188, -23.523, srid=4326)
        cls.prot_cluster = Protocolo.objects.create(
            codigo="PROT-CL-1",
            usuario=cls.cidadao,
            servico=cls.servico_cluster,
            descricao="Com geo cluster",
            status=Protocolo.Status.EM_ANALISE,
            localizacao=ponto,
        )
        cls.prot_sem_cluster = Protocolo.objects.create(
            codigo="PROT-CL-2",
            usuario=cls.cidadao,
            servico=cls.servico_individual,
            descricao="Sem cluster",
            status=Protocolo.Status.EM_ANALISE,
            localizacao=ponto,
        )

    def test_candidatos_cluster_ignora_permite_cluster_false(self):
        ids = set(queryset_candidatos_cluster().values_list("id", flat=True))
        self.assertIn(self.prot_cluster.id, ids)
        self.assertNotIn(self.prot_sem_cluster.id, ids)

    def test_clusterizar_mantém_isolados_mesmo_ponto_e_periodo(self):
        ponto = Point(-46.1881, -23.5231, srid=4326)
        par_a = Protocolo.objects.create(
            codigo="PROT-CL-3A",
            usuario=self.cidadao,
            servico=self.servico_individual,
            descricao="Par A",
            status=Protocolo.Status.EM_ANALISE,
            localizacao=ponto,
        )
        par_b = Protocolo.objects.create(
            codigo="PROT-CL-3B",
            usuario=self.cidadao,
            servico=self.servico_individual,
            descricao="Par B",
            status=Protocolo.Status.EM_ANALISE,
            localizacao=ponto,
        )
        lista = list(
            Protocolo.objects.select_related("servico").filter(
                id__in=[par_a.id, par_b.id]
            )
        )
        clusters = clusterizar_por_servico_e_raio(lista, raio_metros=500)
        self.assertEqual(clusters, [])
        sugestoes = gerar_sugestoes_super_os(raio_metros=500, min_protocolos=2)
        ids_sugeridos = {
            pid
            for s in sugestoes
            for pid in s.get("protocolo_ids", [])
            + s.get("protocolos_envolvidos_ids", [])
        }
        self.assertNotIn(str(par_a.id), ids_sugeridos)
        self.assertNotIn(str(par_b.id), ids_sugeridos)

    def test_duplicar_servico_preserva_permite_cluster(self):
        self.servico_individual.permite_cluster = False
        self.servico_individual.save(update_fields=["permite_cluster"])
        copia = duplicar_servico_catalogo(self.servico_individual)
        self.assertFalse(copia.permite_cluster)


class AvaliacaoProtocoloPwaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cidadao = User.objects.create_user(
            cpf="39053344705",
            password="SenhaForte1!",
            nome="Cidadão CSAT",
            email="csat@test.local",
        )
        cls.outro = User.objects.create_user(
            cpf="15350946056",
            password="SenhaForte1!",
            nome="Outro cidadão",
            email="outro.csat@test.local",
        )
        cls.categoria = CategoriaCatalogo.objects.create(
            nome="Cat CSAT", slug="cat-csat", ativo=True
        )
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cls.categoria, nome="Serv CSAT", ativo=True
        )
        cls.protocolo_aberto = Protocolo.objects.create(
            codigo="PROT-CSAT-AB",
            usuario=cls.cidadao,
            servico=cls.servico,
            descricao="Em andamento",
            status=Protocolo.Status.EM_ANDAMENTO,
        )
        cls.protocolo_resolvido = Protocolo.objects.create(
            codigo="PROT-CSAT-OK",
            usuario=cls.cidadao,
            servico=cls.servico,
            descricao="Concluído",
            status=Protocolo.Status.RESOLVIDO,
        )
        cls.protocolo_outro_usuario = Protocolo.objects.create(
            codigo="PROT-CSAT-OUT",
            usuario=cls.outro,
            servico=cls.servico,
            descricao="De outro",
            status=Protocolo.Status.RESOLVIDO,
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.cidadao)

    def test_recusa_protocolo_nao_resolvido(self):
        url = f"/api/v1/app/protocolos/{self.protocolo_aberto.pk}/avaliar"
        resp = self.client.post(url, {"nota": 5}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recusa_protocolo_de_outro_usuario(self):
        url = f"/api/v1/app/protocolos/{self.protocolo_outro_usuario.pk}/avaliar"
        resp = self.client.post(url, {"nota": 4}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_avaliacao_sucesso(self):
        url = f"/api/v1/app/protocolos/{self.protocolo_resolvido.pk}/avaliar"
        resp = self.client.post(
            url, {"nota": 5, "comentario": "Ótimo atendimento"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        self.assertEqual(resp.data["nota"], 5)
        self.protocolo_resolvido.refresh_from_db()
        self.assertEqual(self.protocolo_resolvido.nota_satisfacao, 5)
        self.assertTrue(
            AvaliacaoProtocolo.objects.filter(protocolo=self.protocolo_resolvido).exists()
        )

    def test_recusa_segunda_avaliacao(self):
        url = f"/api/v1/app/protocolos/{self.protocolo_resolvido.pk}/avaliar"
        self.client.post(url, {"nota": 5}, format="json")
        resp = self.client.post(url, {"nota": 3}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)