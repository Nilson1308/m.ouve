"""Fluxo EM_ANDAMENTO → (setor) → AGUARDANDO_REVISAO → (ouvidoria) → RESOLVIDO."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from atendimentos.backoffice_services import (
    ProtocoloEncerradoError,
    concluir_atendimento_setor,
    garantir_protocolo_tramitavel,
    marcar_ordem_concluida,
    tentar_aguardando_revisao,
)
from atendimentos.models import OrdemServico, Protocolo, ProtocoloHistorico
from catalogo.models import CategoriaCatalogo, ServicoCatalogo, UnidadeAdministrativa

User = get_user_model()


class TramitacaoStatusProtocoloTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cidadao = User.objects.create_user(
            cpf="52998224725",
            password="x",
            nome="Cidadão Tramitação Teste",
            email="cidadao_tram@test.local",
        )
        cls.unidade = UnidadeAdministrativa.objects.create(
            nome="Secretaria Teste",
            sigla="ST",
            ativo=True,
        )
        cls.categoria = CategoriaCatalogo.objects.create(
            nome="Categoria teste tramitação",
            slug="categoria-teste-tram",
            ativo=True,
        )
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Serviço teste tramitação",
            ativo=True,
        )
        cls.protocolo = Protocolo.objects.create(
            codigo="PROT-TEST-001",
            usuario=cls.cidadao,
            servico=cls.servico,
            descricao="Teste de tramitação",
            status=Protocolo.Status.EM_ANDAMENTO,
        )
        cls.ordem = OrdemServico.objects.create(
            protocolo=cls.protocolo,
            unidade=cls.unidade,
            descricao="OS teste",
            status=OrdemServico.Status.EM_ANDAMENTO,
            nome_equipe="Equipe ST",
        )

    def test_setor_finaliza_vai_para_aguardando_revisao(self):
        marcar_ordem_concluida(
            self.ordem,
            despacho_tecnico="Serviço executado conforme norma técnica.",
        )
        mudou = concluir_atendimento_setor(
            self.protocolo,
            self.ordem,
            despacho_tecnico="Serviço executado conforme norma técnica.",
            equipe_nome="Equipe ST",
            unidade_nome="ST",
        )
        self.protocolo.refresh_from_db()

        self.assertTrue(mudou)
        self.assertEqual(self.protocolo.status, Protocolo.Status.AGUARDANDO_REVISAO)
        self.assertNotEqual(self.protocolo.status, Protocolo.Status.RESOLVIDO)

        descricoes = list(
            ProtocoloHistorico.objects.filter(protocolo=self.protocolo).values_list(
                "descricao", flat=True
            )
        )
        texto = " ".join(descricoes)
        self.assertIn("Aguardando validação", texto)
        self.assertIn("Parecer técnico", texto)

    def test_ouvidoria_somente_valida_em_aguardando_revisao(self):
        """tentar_aguardando_revisao nunca define resolvido."""
        marcar_ordem_concluida(self.ordem, despacho_tecnico="Ok")
        tentar_aguardando_revisao(self.protocolo, equipe_nome="ST")
        self.protocolo.refresh_from_db()
        self.assertEqual(self.protocolo.status, Protocolo.Status.AGUARDANDO_REVISAO)

        self.protocolo.status = Protocolo.Status.RESOLVIDO
        self.protocolo.resposta_cidadao = "Encerrado."
        self.protocolo.save(update_fields=["status", "resposta_cidadao", "data_atualizacao"])

        with self.assertRaises(ProtocoloEncerradoError):
            garantir_protocolo_tramitavel(self.protocolo)

        self.protocolo.refresh_from_db()
        self.assertEqual(self.protocolo.status, Protocolo.Status.RESOLVIDO)

    def test_os_pendente_nao_altera_protocolo_para_revisao(self):
        ordem_pendente = OrdemServico.objects.create(
            protocolo=self.protocolo,
            unidade=self.unidade,
            descricao="Segunda OS",
            status=OrdemServico.Status.PENDENTE,
        )
        marcar_ordem_concluida(self.ordem, despacho_tecnico="Parcial")
        mudou = concluir_atendimento_setor(
            self.protocolo,
            self.ordem,
            despacho_tecnico="Parcial",
            equipe_nome="ST",
            unidade_nome="ST",
        )
        self.protocolo.refresh_from_db()

        self.assertFalse(mudou)
        self.assertEqual(self.protocolo.status, Protocolo.Status.EM_ANDAMENTO)
        self.assertEqual(ordem_pendente.status, OrdemServico.Status.PENDENTE)