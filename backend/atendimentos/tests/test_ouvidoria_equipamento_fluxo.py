"""Fluxo Ouvidoria com lookup opcional de equipamentos públicos (chat)."""

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase

from atendimentos.chat_services import finalizar_sessao_com_protocolo
from atendimentos.llm_orchestrator import LLMOrchestrator
from atendimentos.models import MensagemChat, Protocolo, SessaoChat
from atendimentos.services.triagem_service import FONTE_EQUIPAMENTO, executar_triagem_protocolo
from atendimentos.slot_filling_service import aplicar_slot_filling_abertura
from catalogo.datasources import LOOKUP_DATASOURCE_EQUIPAMENTOS
from catalogo.models import CategoriaCatalogo, EquipamentoPublico, ServicoCatalogo, UnidadeAdministrativa

User = get_user_model()


def _schema_ouvidoria_4_passos():
    return {
        "type": "object",
        "properties": {
            "o": {
                "type": "string",
                "title": "Tipo de manifestação",
                "enum": ["reclamacao", "elogio", "sugestao"],
                "enumNames": ["Reclamação", "Elogio", "Sugestão"],
            },
            "q": {
                "type": "string",
                "title": "Área / Tema",
                "enum": ["saude", "educacao", "zeladoria"],
                "enumNames": ["Saúde", "Educação", "Zeladoria"],
            },
            "d": {
                "type": "string",
                "title": "Descrição detalhada",
                "minLength": 10,
            },
            "e": {
                "type": "string",
                "format": "uuid",
                "title": "Equipamento",
                "x-ouvia-datasource": LOOKUP_DATASOURCE_EQUIPAMENTOS,
                "x-ouvia-datasource-filter": {"tipo": "ubs"},
            },
        },
        "required": ["o", "q", "d"],
        "$metadata": {"ordem_campos": ["o", "q", "d", "e"]},
    }


class OuvidoriaEquipamentoFluxoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = CategoriaCatalogo.objects.create(
            nome="Ouvidoria", slug="ouv-equip", ativo=True
        )
        cls.u_saude = UnidadeAdministrativa.objects.create(
            nome="Secretaria de Saúde", sigla="SMS", ativo=True
        )
        cls.ubs_sabauna = EquipamentoPublico.objects.create(
            nome="UBS Sabaúna",
            tipo=EquipamentoPublico.Tipo.UBS,
            unidade_responsavel=cls.u_saude,
            bairro="Sabaúna",
            localizacao=Point(-46.2, -23.7, srid=4326),
            ativo=True,
        )
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Ouvidoria Saúde",
            unidade_responsavel=cls.u_saude,
            ativo=True,
            fluxo_tramitacao=ServicoCatalogo.FluxoTramitacao.OUVIDORIA_ENCAMINHA,
            schema_formulario=_schema_ouvidoria_4_passos(),
        )
        cls.cidadao = User.objects.create_user(
            cpf="52998224725",
            password="x",
            nome="Cidadão Teste",
            email="ouv.equip@test.local",
        )

    def _sessao(self) -> SessaoChat:
        return SessaoChat.objects.create(
            usuario=self.cidadao,
            servico_identificado=self.servico,
            status=SessaoChat.Status.EM_ANDAMENTO,
            dados_coletados={
                "o": "reclamacao",
                "q": "saude",
            },
        )

    def test_match_ubs_preposicao_e_protocolo_com_triagem(self):
        texto = "quero fazer uma reclamação sobre a UBS de Sabaúna"
        sessao = self._sessao()
        MensagemChat.objects.create(
            sessao=sessao, autor=MensagemChat.Autor.CIDADAO, conteudo_texto=texto
        )
        _, aplicados = aplicar_slot_filling_abertura(sessao, self.servico)
        self.assertEqual(aplicados.get("e"), str(self.ubs_sabauna.id))

        sessao.dados_coletados = {
            **(sessao.dados_coletados or {}),
            "o": "reclamacao",
            "q": "saude",
            "d": "Demora no atendimento na unidade de saúde do bairro.",
            "e": str(self.ubs_sabauna.id),
        }
        sessao.save(update_fields=["dados_coletados", "atualizado_em"])

        protocolo = finalizar_sessao_com_protocolo(sessao)
        protocolo.refresh_from_db()
        self.assertEqual(protocolo.equipamento_id, self.ubs_sabauna.id)
        self.assertEqual(protocolo.dados_dinamicos.get("bairro"), "Sabaúna")
        self.assertIsNotNone(protocolo.localizacao)

        triagem = executar_triagem_protocolo(protocolo)
        unidades = triagem.get("unidades_sugeridas") or []
        saude = next((u for u in unidades if u["id"] == str(self.u_saude.id)), None)
        self.assertIsNotNone(saude)
        self.assertEqual(saude["confianca"], 1.0)
        self.assertEqual(saude["fonte"], FONTE_EQUIPAMENTO)

    def test_passo_equipamento_opcional_quando_nao_citado(self):
        sessao = self._sessao()
        sessao.dados_coletados = {
            **(sessao.dados_coletados or {}),
            "d": "Relato sobre fila longa sem citar unidade específica neste momento.",
        }
        sessao.save(update_fields=["dados_coletados", "atualizado_em"])

        turno = LLMOrchestrator().passo_deterministico_preenchimento(sessao)
        self.assertEqual(turno.acao_ui, "escolha_campo")
        self.assertIsNotNone(turno.config_escolha)
        self.assertEqual(turno.config_escolha.get("campo"), "e")
        self.assertEqual(turno.config_escolha.get("datasource"), LOOKUP_DATASOURCE_EQUIPAMENTOS)
        self.assertTrue(turno.config_escolha.get("opcional"))

    def test_pular_equipamento_opcional_avanca_para_revisao(self):
        from atendimentos.chat_estado import registrar_campo_pulado, set_meta
        from atendimentos.chat_estado import FaseChat

        sessao = self._sessao()
        set_meta(sessao, fase=FaseChat.PREENCHIMENTO)
        sessao.dados_coletados = {
            **(sessao.dados_coletados or {}),
            "d": "Problema geral na rede municipal de saúde, sem unidade definida.",
        }
        sessao.save(update_fields=["dados_coletados", "atualizado_em"])
        registrar_campo_pulado(sessao, "e")
        sessao.refresh_from_db()

        turno = LLMOrchestrator().passo_deterministico_preenchimento(sessao)
        self.assertTrue(turno.ir_para_revisao or turno.acao_ui == "revisao_final")