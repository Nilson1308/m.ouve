"""Resiliência do chat RAG — campos opcionais, equipamento, troca de categoria e tom."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase

from atendimentos.chat_estado import FaseChat, get_meta, set_meta
from atendimentos.chat_services import finalizar_sessao_com_protocolo
from atendimentos.chat_intencao import detectar_intencao_pular_ou_nao_sei
from atendimentos.llm_orchestrator import (
    LLMOrchestrator,
    _campos_faltantes,
    _texto_pergunta_campo,
    _titulo_apenas_cru,
)
from atendimentos.models import SessaoChat
from atendimentos.services.chat_equipamento_lookup import aplicar_equipamento_em_texto_usuario
from catalogo.datasources import LOOKUP_DATASOURCE_EQUIPAMENTOS
from catalogo.models import CategoriaCatalogo, EquipamentoPublico, ServicoCatalogo, UnidadeAdministrativa
from catalogo.validators import validar_dados_dinamicos

User = get_user_model()


SCHEMA_OBS_OPCIONAL = {
    "type": "object",
    "properties": {
        "tipo_falha": {"type": "string", "title": "Tipo"},
        "observacoes": {
            "type": "string",
            "title": "Observações Adicionais",
        },
        "localizacao": {
            "type": "string",
            "title": "Local",
            "x-ouvia-tipo-campo": "geolocation",
        },
    },
    "required": ["tipo_falha", "localizacao"],
    "$metadata": {"ordem_campos": ["tipo_falha", "observacoes", "localizacao"]},
}


SCHEMA_EQUIP_OPCIONAL = {
    "type": "object",
    "properties": {
        "o": {"type": "string", "title": "Tipo", "enum": ["reclamacao"]},
        "d": {"type": "string", "title": "Descreva sua manifestação", "minLength": 8},
        "i": {
            "type": "string",
            "format": "uuid",
            "title": "Informe o equipamento público",
            "x-ouvia-datasource": LOOKUP_DATASOURCE_EQUIPAMENTOS,
        },
        "localizacao": {
            "type": "string",
            "x-ouvia-tipo-campo": "geolocation",
        },
    },
    "required": ["o", "d", "localizacao"],
    "$metadata": {"ordem_campos": ["o", "d", "i", "localizacao"]},
}


class DetectarIntencaoPularTests(TestCase):
    def test_frases_opcionais(self):
        self.assertTrue(
            detectar_intencao_pular_ou_nao_sei("não sei", obrigatorio=False, usar_llm=False)
        )
        self.assertTrue(
            detectar_intencao_pular_ou_nao_sei(
                "sem observação", obrigatorio=False, usar_llm=False
            )
        )


class CampoOpcionalAvancoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            cpf="52987654321",
            password="x",
            nome="Teste RAG",
            email="rag1@test.local",
        )
        cat = CategoriaCatalogo.objects.create(
            nome="Zel RAG", slug="zel-rag", tipo_legado="zeladoria", ativo=True
        )
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Iluminação RAG",
            schema_formulario=SCHEMA_OBS_OPCIONAL,
            ativo=True,
            sla_horas=48,
        )

    def _sessao(self) -> SessaoChat:
        s = SessaoChat.objects.create(
            usuario=self.user,
            categoria_inicial="Zeladoria",
            servico_identificado=self.servico,
            dados_coletados={"tipo_falha": "lampada"},
        )
        set_meta(s, fase=FaseChat.PREENCHIMENTO)
        s.save()
        return s

    def test_nao_sei_pula_observacoes(self):
        sessao = self._sessao()
        orch = LLMOrchestrator()
        turno = orch._estagio_slot_filling(sessao, texto_usuario="não sei", anexos_novos=0)
        sessao.refresh_from_db()
        pulados = (sessao.dados_coletados or {}).get("_campos_pulados") or []
        self.assertIn("observacoes", pulados)
        faltantes = _campos_faltantes(self.servico, sessao.dados_coletados or {}, sessao)
        self.assertNotIn("observacoes", faltantes)
        self.assertEqual(faltantes[0], "localizacao")
        self.assertIn(turno.acao_ui, ("solicitar_localizacao", None))

    def test_sem_observacao_pula(self):
        sessao = self._sessao()
        orch = LLMOrchestrator()
        orch._estagio_slot_filling(sessao, texto_usuario="sem observação", anexos_novos=0)
        sessao.refresh_from_db()
        pulados = (sessao.dados_coletados or {}).get("_campos_pulados") or []
        self.assertIn("observacoes", pulados)


class EquipamentoNaoCatalogadoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            cpf="62198765432",
            password="x",
            nome="Teste EQ",
            email="rag2@test.local",
        )
        cls.cat = CategoriaCatalogo.objects.create(
            nome="Ouv RAG", slug="ouv-rag", ativo=True
        )
        cls.unidade = UnidadeAdministrativa.objects.create(
            nome="SMS RAG", sigla="SMSR", ativo=True
        )
        EquipamentoPublico.objects.create(
            nome="UBS Conhecida",
            tipo=EquipamentoPublico.Tipo.UBS,
            unidade_responsavel=cls.unidade,
            bairro="Centro",
            ativo=True,
            localizacao=Point(-42.0, -22.0, srid=4326),
        )
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cls.cat,
            nome="Ouvidoria RAG",
            unidade_responsavel=cls.unidade,
            schema_formulario=SCHEMA_EQUIP_OPCIONAL,
            ativo=True,
        )

    def _sessao_preenchimento(self) -> SessaoChat:
        s = SessaoChat.objects.create(
            usuario=self.user,
            servico_identificado=self.servico,
            dados_coletados={
                "o": "reclamacao",
                "d": "reclamação sobre demora no atendimento",
                "_localizacao": {
                    "latitude": -22.0,
                    "longitude": -42.0,
                    "endereco": "Rua Teste",
                },
                "localizacao": "confirmada",
            },
        )
        set_meta(s, fase=FaseChat.PREENCHIMENTO)
        s.save()
        return s

    def test_texto_livre_nao_gera_erro_uuid(self):
        texto = "UBS Jardim Maricá"
        aplicados = aplicar_equipamento_em_texto_usuario(self._sessao_preenchimento(), self.servico, texto)
        self.assertIn("i", aplicados)
        val = aplicados["i"]
        self.assertIsInstance(val, dict)
        self.assertTrue(val.get("nao_catalogado"))
        self.assertIn("Jardim", val.get("texto", ""))
        dados = {
            "o": "reclamacao",
            "d": "x" * 12,
            "i": val,
            "localizacao": "confirmada",
        }
        validar_dados_dinamicos(self.servico.schema_formulario, dados)

    def test_protocolo_grava_equipamento_citado(self):
        sessao = self._sessao_preenchimento()
        nome = "UBS Jardim Maricá"
        aplicados = aplicar_equipamento_em_texto_usuario(sessao, self.servico, nome)
        dados = dict(sessao.dados_coletados or {})
        dados.update(aplicados)
        sessao.dados_coletados = dados
        sessao.save()
        set_meta(sessao, fase=FaseChat.REVISAO)
        sessao.save()
        protocolo = finalizar_sessao_com_protocolo(sessao)
        self.assertEqual(protocolo.equipamento_citado_nao_catalogado, nome)
        self.assertIsNone(protocolo.equipamento_id)


class TrocaCategoriaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            cpf="73219876543",
            password="x",
            nome="Teste Cat",
            email="rag3@test.local",
        )
        cls.cat_ouv = CategoriaCatalogo.objects.create(
            nome="Ouvidoria RAG", slug="ouv-rag-x", ativo=True
        )
        cls.cat_zel = CategoriaCatalogo.objects.create(
            nome="Zeladoria RAG", slug="zel-rag-x", tipo_legado="zeladoria", ativo=True
        )
        cls.svc_ouv = ServicoCatalogo.objects.create(
            categoria=cls.cat_ouv,
            nome="Manifestação geral",
            ativo=True,
            schema_formulario={"type": "object", "properties": {}, "required": []},
        )
        cls.svc_zel = ServicoCatalogo.objects.create(
            categoria=cls.cat_zel,
            nome="Tapa-buraco",
            ativo=True,
            schema_formulario={"type": "object", "properties": {}, "required": []},
        )

    def test_classificacao_sugere_troca(self):
        sessao = SessaoChat.objects.create(
            usuario=self.user,
            categoria_inicial="Ouvidoria RAG",
        )
        fake = {
            "servico_id": str(self.svc_zel.id),
            "confianca": 0.9,
            "acao_ui": "confirmar_servico",
            "resposta_cidadao": "Parece ser uma demanda de zeladoria.",
        }
        with patch(
            "atendimentos.llm_orchestrator._chamar_json_estruturado",
            return_value=fake,
        ):
            turno = LLMOrchestrator()._estagio_classificacao(
                sessao, texto_usuario="tem um buraco enorme na rua das flores"
            )
        self.assertEqual(turno.acao_ui, "sugerir_troca_categoria")
        self.assertEqual(turno.payload_ui.get("tipo_acao"), "sugerir_troca_categoria")
        self.assertEqual(
            turno.payload_ui.get("categoria_sugerida", {}).get("slug"),
            self.cat_zel.slug,
        )

    def test_recusar_troca_marca_forcar_categoria(self):
        sessao = SessaoChat.objects.create(
            usuario=self.user,
            categoria_inicial="Ouvidoria RAG",
            servico_identificado=self.svc_ouv,
            dados_coletados={"_meta": {"fase": FaseChat.PREENCHIMENTO}},
        )
        set_meta(sessao, fase=FaseChat.PREENCHIMENTO)
        sessao.save()
        set_meta(
            sessao,
            troca_categoria_pendente={
                "servico_sugerido": {"id": str(self.svc_zel.id)},
            },
        )
        sessao.save()
        turno = LLMOrchestrator().processar_turno(
            sessao,
            texto_usuario="",
            dados_slot={"forcar_categoria_atual": True},
        )
        sessao.refresh_from_db()
        meta = get_meta(sessao)
        self.assertTrue(meta.get("forcar_categoria_atual"))
        self.assertIsNone(meta.get("troca_categoria_pendente"))
        self.assertNotEqual(turno.acao_ui, "sugerir_troca_categoria")


class PerguntaHumanizadaTests(TestCase):
    def test_titulo_cru_ativa_fallback(self):
        prop = {"type": "string", "title": "Observações Adicionais"}
        self.assertTrue(_titulo_apenas_cru(prop))
        texto = _texto_pergunta_campo(prop, "observacoes", opcional=True)
        self.assertNotEqual(texto, "Observações Adicionais")
        self.assertIn("observação", texto.lower())

    def test_foto_opcional_nao_ecoa_titulo(self):
        prop = {
            "type": "string",
            "title": "Enviar foto",
            "x-ouvia-tipo-campo": "image",
        }
        self.assertTrue(_titulo_apenas_cru(prop))
        texto = _texto_pergunta_campo(prop, "foto", opcional=True)
        self.assertNotEqual(texto, "Enviar foto")
        self.assertIn("foto", texto.lower())

    def test_descricao_obrigatoria(self):
        prop = {"type": "string", "title": "Descreva sua manifestação", "minLength": 10}
        texto = _texto_pergunta_campo(prop, "d", opcional=False)
        self.assertNotEqual(texto, "Descreva sua manifestação")
        self.assertGreater(len(texto), 20)