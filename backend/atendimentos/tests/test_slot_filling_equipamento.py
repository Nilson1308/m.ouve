"""Slot filling determinístico — equipamentos públicos."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from atendimentos.models import SessaoChat
from atendimentos.slot_filling_service import (
    aplicar_slot_filling_abertura,
    preencher_equipamento_por_texto_inicial,
)
from catalogo.datasources import LOOKUP_DATASOURCE_EQUIPAMENTOS
from catalogo.models import CategoriaCatalogo, EquipamentoPublico, ServicoCatalogo, UnidadeAdministrativa

User = get_user_model()


class SlotFillingEquipamentoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = CategoriaCatalogo.objects.create(
            nome="Cat Slot", slug="cat-slot-eq", ativo=True
        )
        cls.u = UnidadeAdministrativa.objects.create(
            nome="Secretaria", sigla="SEC", ativo=True
        )
        cls.ubs_a = EquipamentoPublico.objects.create(
            nome="UBS Vila Progresso",
            tipo=EquipamentoPublico.Tipo.UBS,
            unidade_responsavel=cls.u,
            apelidos=["Postinho da Vila"],
            ativo=True,
        )
        cls.ubs_b = EquipamentoPublico.objects.create(
            nome="UBS Vila Esperança",
            tipo=EquipamentoPublico.Tipo.UBS,
            unidade_responsavel=cls.u,
            apelidos=["Postinho Esperança"],
            ativo=True,
        )
        cls.schema = {
            "type": "object",
            "properties": {
                "local_atendimento": {
                    "type": "string",
                    "format": "uuid",
                    "x-ouvia-datasource": LOOKUP_DATASOURCE_EQUIPAMENTOS,
                    "x-ouvia-datasource-filter": {"tipo": "ubs"},
                },
            },
        }
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Serviço",
            unidade_responsavel=cls.u,
            ativo=True,
            schema_formulario=cls.schema,
        )
        cls.cidadao = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Cidadão",
            email="slot.eq@test.local",
        )

    def _sessao(self, texto: str) -> SessaoChat:
        return SessaoChat.objects.create(
            usuario=self.cidadao,
            servico_identificado=self.servico,
            status=SessaoChat.Status.EM_ANDAMENTO,
            dados_coletados={},
        )

    def test_match_unico_por_apelido(self):
        texto = "Quero reclamar do atendimento no Postinho da Vila ontem à tarde."
        campos = preencher_equipamento_por_texto_inicial(self.servico, texto, {})
        self.assertEqual(campos.get("local_atendimento"), str(self.ubs_a.id))

    def test_match_preposicao_ubs_sabauna(self):
        ubs_sabauna = EquipamentoPublico.objects.create(
            nome="UBS Sabaúna",
            tipo=EquipamentoPublico.Tipo.UBS,
            unidade_responsavel=self.u,
            ativo=True,
        )
        texto = "quero fazer uma reclamação sobre a UBS de Sabaúna"
        campos = preencher_equipamento_por_texto_inicial(self.servico, texto, {})
        self.assertEqual(campos.get("local_atendimento"), str(ubs_sabauna.id))

    def test_ambiguidade_nao_preenche(self):
        texto = (
            "Problema num postinho municipal com fila grande — não sei qual unidade "
            "mas quero registrar oficialmente minha insatisfação."
        )
        campos = preencher_equipamento_por_texto_inicial(self.servico, texto, {})
        self.assertEqual(campos, {})