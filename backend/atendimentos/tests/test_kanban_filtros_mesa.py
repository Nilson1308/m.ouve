"""Filtros do Kanban unificado alinhados à listagem de protocolos."""

from django.contrib.auth import get_user_model
from django.http import QueryDict
from django.test import TestCase

from atendimentos.kanban_services import montar_kanban_unificado, resumo_contadores_mesa
from atendimentos.models import Protocolo
from catalogo.models import CategoriaCatalogo, ServicoCatalogo, UnidadeAdministrativa
from core_auth.models import PerfilAcesso

User = get_user_model()


class KanbanFiltrosMesaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.unidade = UnidadeAdministrativa.objects.create(
            nome="Sec Teste", sigla="TST", ativo=True
        )
        cat = CategoriaCatalogo.objects.create(
            nome="Cat", slug="cat-kanban", tipo_legado="zeladoria", ativo=True
        )
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Serv",
            unidade_responsavel=cls.unidade,
            schema_formulario={"type": "object", "properties": {}},
            ativo=True,
            sla_horas=24,
        )
        perfil = PerfilAcesso.objects.create(
            codigo="super_kanban_filtro",
            nome="Super",
            permissoes={"regras": {"super_admin": True, "acesso_staff": True}},
        )
        cls.super = User.objects.create_user(
            cpf="99988877766",
            password="x",
            nome="Super",
            email="super-kanban@test.local",
            is_staff=True,
        )
        cls.super.perfil_acesso = perfil
        cls.super.save()
        cls.cidadao = User.objects.create_user(
            cpf="88877766655",
            password="x",
            nome="Cid",
            email="cid@test.local",
        )

    def test_filtra_urgencia_pelo_campo_matriz(self):
        p_crit = Protocolo.objects.create(
            codigo="P-K-CRIT",
            usuario=self.cidadao,
            servico=self.servico,
            descricao="Crítico",
            status=Protocolo.Status.EM_ANALISE,
            urgencia=Protocolo.Urgencia.CRITICA,
            dados_dinamicos={},
        )
        p_norm = Protocolo.objects.create(
            codigo="P-K-NORM",
            usuario=self.cidadao,
            servico=self.servico,
            descricao="Normal",
            status=Protocolo.Status.EM_ANALISE,
            urgencia=Protocolo.Urgencia.NORMAL,
            dados_dinamicos={},
        )
        q = QueryDict(mutable=True)
        q.setlist("urgencia", ["critica"])
        itens = montar_kanban_unificado(q, user=self.super)
        codigos = [i["codigo"] for i in itens if i.get("tipo") == "protocolo"]
        self.assertIn(p_crit.codigo, codigos)
        self.assertNotIn(p_norm.codigo, codigos)

    def test_filtra_servico_id(self):
        p = Protocolo.objects.create(
            codigo="P-K-SRV",
            usuario=self.cidadao,
            servico=self.servico,
            descricao="x",
            status=Protocolo.Status.EM_ANALISE,
        )
        q = QueryDict(mutable=True)
        q.setlist("servico_id", [str(self.servico.id)])
        itens = montar_kanban_unificado(q, user=self.super)
        codigos = [i["codigo"] for i in itens if i.get("tipo") == "protocolo"]
        self.assertIn(p.codigo, codigos)

    def test_resumo_contadores_respeita_filtro_urgencia(self):
        Protocolo.objects.create(
            codigo="P-K-R1",
            usuario=self.cidadao,
            servico=self.servico,
            descricao="c",
            status=Protocolo.Status.EM_ANALISE,
            urgencia=Protocolo.Urgencia.CRITICA,
        )
        Protocolo.objects.create(
            codigo="P-K-R2",
            usuario=self.cidadao,
            servico=self.servico,
            descricao="n",
            status=Protocolo.Status.EM_ANALISE,
            urgencia=Protocolo.Urgencia.NORMAL,
        )
        q = QueryDict(mutable=True)
        q.setlist("urgencia", ["critica"])
        itens = montar_kanban_unificado(q, user=self.super)
        resumo = resumo_contadores_mesa(itens, user=self.super, params=q)
        self.assertEqual(resumo["total_itens"], 1)
        self.assertEqual(resumo["criticos"], 1)

    def test_busca_multiplos_codigos_radar(self):
        p1 = Protocolo.objects.create(
            codigo="PROT-2026-001",
            usuario=self.cidadao,
            servico=self.servico,
            descricao="um",
            status=Protocolo.Status.EM_ANALISE,
        )
        p2 = Protocolo.objects.create(
            codigo="PROT-2026-002",
            usuario=self.cidadao,
            servico=self.servico,
            descricao="dois",
            status=Protocolo.Status.EM_ANALISE,
        )
        Protocolo.objects.create(
            codigo="PROT-2026-099",
            usuario=self.cidadao,
            servico=self.servico,
            descricao="outro",
            status=Protocolo.Status.EM_ANALISE,
        )
        q = QueryDict(mutable=True)
        q["busca"] = "PROT-2026-001 PROT-2026-002"
        q["status"] = "em_analise"
        itens = montar_kanban_unificado(q, user=self.super)
        codigos = {i["codigo"] for i in itens if i.get("tipo") == "protocolo"}
        self.assertEqual(codigos, {p1.codigo, p2.codigo})