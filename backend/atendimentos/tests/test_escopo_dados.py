"""Governança de dados — escopo de protocolos por unidade (sem hardcode de perfil)."""

from django.contrib.auth import get_user_model

from atendimentos.models import OrdemServico, Protocolo
from atendimentos.services.escopo_dados import queryset_protocolos_escopo
from catalogo.models import CategoriaCatalogo, ServicoCatalogo, UnidadeAdministrativa
from core_auth.models import PerfilAcesso
from core_auth.rbac import aplicar_regras_automaticas, permissoes_padrao
from django.test import TestCase

User = get_user_model()


def _perfil_municipio():
    base = permissoes_padrao()
    base["mesa_trabalho"] = {"ler": True, "criar": True, "editar": True, "excluir": False}
    return aplicar_regras_automaticas(base)


def _perfil_vinculo_unidade():
    base = permissoes_padrao()
    base["painel_setorial"] = {"ler": True, "criar": False, "editar": True, "excluir": False}
    base["mesa_trabalho"] = {"ler": True, "criar": False, "editar": False, "excluir": False}
    return aplicar_regras_automaticas(base, requer_vinculo=True)


class EscopoProtocolosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cidadao = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Cidadão Escopo",
            email="cidadao.escopo@test.local",
        )
        cls.unidade_a = UnidadeAdministrativa.objects.create(
            nome="Unidade A", sigla="UA", ativo=True
        )
        cls.unidade_b = UnidadeAdministrativa.objects.create(
            nome="Unidade B", sigla="UB", ativo=True
        )
        cls.categoria = CategoriaCatalogo.objects.create(
            nome="Cat escopo",
            slug="cat-escopo",
            ativo=True,
        )
        cls.servico_a = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Serviço A",
            unidade_responsavel=cls.unidade_a,
            ativo=True,
        )
        cls.servico_b = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Serviço B",
            unidade_responsavel=cls.unidade_b,
            ativo=True,
        )

        cls.perfil_ouvidor = PerfilAcesso.objects.create(
            codigo="teste_ouvidor_escopo",
            nome="Ouvidor teste escopo",
            permissoes=_perfil_municipio(),
            ativo=True,
        )
        cls.perfil_setorial = PerfilAcesso.objects.create(
            codigo="teste_custom_setorial",
            nome="Perfil custom com unidade",
            permissoes=_perfil_vinculo_unidade(),
            ativo=True,
        )

        cls.ouvidor = User.objects.create_user(
            cpf="15350946056",
            password="x",
            nome="Ouvidor Escopo",
            email="ouvidor.escopo@test.local",
            perfil_acesso=cls.perfil_ouvidor,
            is_staff=True,
        )
        cls.operador_a = User.objects.create_user(
            cpf="52998224725",
            password="x",
            nome="Operador A",
            email="operador.a@test.local",
            perfil_acesso=cls.perfil_setorial,
            unidade=cls.unidade_a,
            is_staff=True,
        )
        cls.gestor_a = User.objects.create_user(
            cpf="11144477735",
            password="x",
            nome="Gestor A",
            email="gestor.a@test.local",
            perfil_acesso=cls.perfil_setorial,
            unidade=cls.unidade_a,
            is_staff=True,
        )

        cls.protocolo_somente_b = Protocolo.objects.create(
            codigo="PROT-ESC-B",
            usuario=cls.cidadao,
            servico=cls.servico_b,
            descricao="Exclusivo unidade B",
            status=Protocolo.Status.EM_ANALISE,
        )
        cls.protocolo_b_com_os_a = Protocolo.objects.create(
            codigo="PROT-ESC-OS",
            usuario=cls.cidadao,
            servico=cls.servico_b,
            descricao="Nasceu em B, despachado para A",
            status=Protocolo.Status.EM_ANDAMENTO,
        )
        OrdemServico.objects.create(
            protocolo=cls.protocolo_b_com_os_a,
            unidade=cls.unidade_a,
            descricao="OS para unidade A",
            status=OrdemServico.Status.EM_ANDAMENTO,
        )
        cls.protocolo_somente_a = Protocolo.objects.create(
            codigo="PROT-ESC-A",
            usuario=cls.cidadao,
            servico=cls.servico_a,
            descricao="Exclusivo unidade A",
            status=Protocolo.Status.EM_ANALISE,
        )

    def _ids(self, user):
        return set(queryset_protocolos_escopo(user).values_list("id", flat=True))

    def test_ouvidor_ve_todas_as_unidades(self):
        ids = self._ids(self.ouvidor)
        self.assertIn(self.protocolo_somente_a.id, ids)
        self.assertIn(self.protocolo_somente_b.id, ids)
        self.assertIn(self.protocolo_b_com_os_a.id, ids)
        self.assertEqual(len(ids), 3)

    def test_operador_unidade_a_nao_ve_exclusivo_unidade_b(self):
        ids = self._ids(self.operador_a)
        self.assertIn(self.protocolo_somente_a.id, ids)
        self.assertIn(self.protocolo_b_com_os_a.id, ids)
        self.assertNotIn(self.protocolo_somente_b.id, ids)

    def test_gestor_unidade_a_ve_protocolo_b_despachado_via_os(self):
        ids = self._ids(self.gestor_a)
        self.assertIn(self.protocolo_b_com_os_a.id, ids)
        self.assertNotIn(self.protocolo_somente_b.id, ids)