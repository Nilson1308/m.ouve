"""
E2E reprodutor — Ouvidoria 4 passos, campo ``i`` (equipamentos_publicos).
"""

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase

from atendimentos.chat_estado import FaseChat, set_meta
from atendimentos.chat_services import finalizar_sessao_com_protocolo
from atendimentos.llm_orchestrator import LLMOrchestrator, _campos_faltantes, _dados_negocio
from atendimentos.lookup_campos import higienizar_lookup_na_sessao
from atendimentos.models import MensagemChat, SessaoChat
from atendimentos.services.triagem_service import FONTE_EQUIPAMENTO, executar_triagem_protocolo
from atendimentos.slot_filling_service import aplicar_slot_filling_abertura
from catalogo.datasources import LOOKUP_DATASOURCE_EQUIPAMENTOS
from catalogo.models import CategoriaCatalogo, EquipamentoPublico, ServicoCatalogo, UnidadeAdministrativa

User = get_user_model()

def schema_ouvidoria_producao() -> dict:
    """Espelha o schema publicado (chaves o, q, d, i)."""
    return {
        "type": "object",
        "properties": {
            "o": {
                "type": "string",
                "title": "O que deseja manifestar?",
                "enum": ["reclamacao", "elogio", "sugestao"],
            },
            "q": {
                "type": "string",
                "title": "Qual área/setor?",
                "enum": ["saude", "educacao", "zeladoria"],
            },
            "d": {
                "type": "string",
                "title": "Descreva sua manifestação",
                "minLength": 10,
            },
            "i": {
                "type": "string",
                "format": "uuid",
                "title": "Informe o equipamento público",
                "x-ouvia-datasource": LOOKUP_DATASOURCE_EQUIPAMENTOS,
            },
        },
        "required": ["o", "q", "d"],
        "$metadata": {"ordem_campos": ["o", "q", "d", "i"]},
    }


class FluxoOuvidoriaEquipamentoE2ETests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = CategoriaCatalogo.objects.create(
            nome="Ouvidoria E2E", slug="ouv-e2e-eq", ativo=True
        )
        cls.u_saude = UnidadeAdministrativa.objects.create(
            nome="Secretaria de Saúde", sigla="SMS", ativo=True
        )
        cls.ubs = EquipamentoPublico.objects.create(
            nome="UBS Sabaúna",
            tipo=EquipamentoPublico.Tipo.UBS,
            unidade_responsavel=cls.u_saude,
            bairro="Sabaúna",
            apelidos=["UBS Sabaúna", "Unidade Básica de Saúde de Sabaúna"],
            localizacao=Point(-46.211, -23.523, srid=4326),
            ativo=True,
        )
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Ouvidoria E2E",
            unidade_responsavel=cls.u_saude,
            ativo=True,
            fluxo_tramitacao=ServicoCatalogo.FluxoTramitacao.OUVIDORIA_ENCAMINHA,
            schema_formulario=schema_ouvidoria_producao(),
        )
        cls.cidadao = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Cidadão E2E",
            email="e2e.ouv@test.local",
        )

    def _nova_sessao(self) -> SessaoChat:
        sessao = SessaoChat.objects.create(
            usuario=self.cidadao,
            servico_identificado=self.servico,
            status=SessaoChat.Status.EM_ANDAMENTO,
            dados_coletados={},
        )
        set_meta(sessao, fase=FaseChat.PREENCHIMENTO)
        return sessao

    def test_cenario_a_ubs_na_primeira_frase_com_gps_dispositivo(self):
        m1 = "quero fazer uma reclamação sobre a UBS de Sabaúna"
        descricao = (
            "estive na UBS para retirar minha medicação, esperei mais de 2h para o atendente "
            "da farmácia informar que minha medicação não estava disponível."
        )
        sessao = self._nova_sessao()
        MensagemChat.objects.create(
            sessao=sessao, autor=MensagemChat.Autor.CIDADAO, conteudo_texto=m1
        )
        MensagemChat.objects.create(
            sessao=sessao, autor=MensagemChat.Autor.CIDADAO, conteudo_texto="sim"
        )

        _, app_abertura = aplicar_slot_filling_abertura(sessao, self.servico)
        self.assertEqual(app_abertura.get("i"), str(self.ubs.id))

        dados = dict(sessao.dados_coletados or {})
        dados.update({"o": "reclamacao", "q": "saude", "d": descricao})
        # Simula LLM gravando texto livre no lookup (bug de produção)
        dados["i"] = "UBS de Sabaúna"
        dados["_localizacao"] = {
            "latitude": -23.516,
            "longitude": -46.185,
            "endereco": "Conjunto Habitacional Brás Cubas",
        }
        sessao.dados_coletados = dados
        sessao.save(update_fields=["dados_coletados", "atualizado_em"])

        higienizar_lookup_na_sessao(sessao)
        sessao.refresh_from_db()
        turno = LLMOrchestrator().passo_deterministico_preenchimento(sessao)
        sessao.refresh_from_db()
        self.assertEqual(_campos_faltantes(self.servico, _dados_negocio(sessao), sessao), [])
        self.assertTrue(
            turno.ir_para_revisao or turno.acao_ui == "revisao_final",
            msg=f"Esperava revisão, veio {turno.acao_ui}",
        )
        self.assertEqual((sessao.dados_coletados or {}).get("i"), str(self.ubs.id))

        protocolo = finalizar_sessao_com_protocolo(sessao)
        protocolo.refresh_from_db()
        self.assertEqual(protocolo.equipamento_id, self.ubs.id)
        self.assertEqual(protocolo.dados_dinamicos.get("bairro"), "Sabaúna")
        self.assertEqual(str(protocolo.dados_dinamicos.get("i")), str(self.ubs.id))

        triagem = executar_triagem_protocolo(protocolo)
        saude = next(
            (
                u
                for u in (triagem.get("unidades_sugeridas") or [])
                if u["id"] == str(self.u_saude.id)
            ),
            None,
        )
        self.assertIsNotNone(saude)
        self.assertEqual(saude["fonte"], FONTE_EQUIPAMENTO)
        self.assertEqual(saude["confianca"], 1.0)

    def test_cenario_b_deve_perguntar_passo_4(self):
        sessao = self._nova_sessao()
        MensagemChat.objects.create(
            sessao=sessao,
            autor=MensagemChat.Autor.CIDADAO,
            conteudo_texto="quero fazer uma reclamação sobre atendimento na saúde",
        )
        sessao.dados_coletados = {
            "o": "reclamacao",
            "q": "saude",
            "d": "Relato sobre demora e falta de medicamento sem citar unidade específica.",
        }
        sessao.save(update_fields=["dados_coletados", "atualizado_em"])

        turno = LLMOrchestrator().passo_deterministico_preenchimento(sessao)
        self.assertEqual(turno.acao_ui, "escolha_campo")
        self.assertEqual(turno.config_escolha.get("campo"), "i")
        self.assertEqual(
            turno.config_escolha.get("datasource"), LOOKUP_DATASOURCE_EQUIPAMENTOS
        )
        self.assertTrue(turno.config_escolha.get("opcional"))