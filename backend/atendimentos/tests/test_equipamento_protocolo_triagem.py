"""Vínculo equipamento → protocolo e triagem."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from atendimentos.models import Protocolo
from atendimentos.services.equipamento_protocolo import sincronizar_equipamento_no_protocolo
from atendimentos.services.triagem_service import (
    FONTE_EQUIPAMENTO,
    executar_triagem_protocolo,
    montar_triagem_sugerida,
)
from catalogo.datasources import LOOKUP_DATASOURCE_EQUIPAMENTOS
from catalogo.models import CategoriaCatalogo, EquipamentoPublico, ServicoCatalogo, UnidadeAdministrativa

User = get_user_model()


class EquipamentoProtocoloTriagemTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = CategoriaCatalogo.objects.create(
            nome="Cat Equip", slug="cat-equip", ativo=True
        )
        cls.u_saude = UnidadeAdministrativa.objects.create(
            nome="Secretaria de Saúde", sigla="SMS", ativo=True
        )
        cls.ubs = EquipamentoPublico.objects.create(
            nome="UBS Norte",
            tipo=EquipamentoPublico.Tipo.UBS,
            unidade_responsavel=cls.u_saude,
            ativo=True,
        )
        cls.schema = {
            "type": "object",
            "properties": {
                "equipamento_saude": {
                    "type": "string",
                    "format": "uuid",
                    "x-ouvia-datasource": LOOKUP_DATASOURCE_EQUIPAMENTOS,
                },
            },
        }
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Ouvidoria Saúde",
            unidade_responsavel=cls.u_saude,
            ativo=True,
            fluxo_tramitacao=ServicoCatalogo.FluxoTramitacao.OUVIDORIA_ENCAMINHA,
            schema_formulario=cls.schema,
        )
        cls.cidadao = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Cidadão",
            email="cid.equip@test.local",
        )

    def test_sincroniza_equipamento_e_triagem(self):
        protocolo = Protocolo.objects.create(
            codigo=Protocolo.gerar_codigo(),
            usuario=self.cidadao,
            servico=self.servico,
            dados_dinamicos={"equipamento_saude": str(self.ubs.id)},
            descricao="Teste equipamento",
            status=Protocolo.Status.EM_ANALISE,
        )
        sincronizar_equipamento_no_protocolo(protocolo)
        protocolo.refresh_from_db()
        self.assertEqual(protocolo.equipamento_id, self.ubs.id)

        payload = executar_triagem_protocolo(protocolo)
        unidades = payload.get("unidades_sugeridas") or []
        self.assertTrue(unidades)
        fontes = {u["fonte"] for u in unidades}
        self.assertIn(FONTE_EQUIPAMENTO, fontes)
        saude = next(u for u in unidades if u["id"] == str(self.u_saude.id))
        self.assertEqual(saude["confianca"], 1.0)
        self.assertIn("Equipamento", saude["motivo"])