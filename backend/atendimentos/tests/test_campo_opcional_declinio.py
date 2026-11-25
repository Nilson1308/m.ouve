"""Campo opcional — cidadão declina informação (sem loop de repescagem)."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from atendimentos.chat_estado import (
    FaseChat,
    get_fase,
    registrar_campo_pulado,
    set_meta,
    usuario_declina_informacao_campo,
)
from atendimentos.chat_services import _requisitos_revisao_ok
from atendimentos.llm_orchestrator import (
    LLMOrchestrator,
    MSG_REVISAO,
    _anexo_sessao_obrigatorio,
    _campos_faltantes,
)
from atendimentos.models import SessaoChat
from catalogo.models import CategoriaCatalogo, ServicoCatalogo

User = get_user_model()

SCHEMA_ILUMINACAO = {
    "type": "object",
    "properties": {
        "tipo_falha": {"type": "string", "title": "Tipo"},
        "numero_poste": {
            "type": "string",
            "title": "Número do poste (se houver)",
            "x-ouvia-ui-pergunta": "Qual é o número do poste, se houver?",
        },
        "localizacao": {
            "type": "string",
            "title": "Local",
            "x-ouvia-tipo-campo": "geolocation",
        },
    },
    "required": ["tipo_falha", "localizacao"],
    "$metadata": {
        "ordem_campos": ["tipo_falha", "numero_poste", "localizacao"],
        "exige_localizacao": True,
    },
}


class UsuarioDeclinaInformacaoTests(TestCase):
    def test_frases_reconhecidas(self):
        self.assertTrue(usuario_declina_informacao_campo("não tenho a informação"))
        self.assertTrue(usuario_declina_informacao_campo("nao tenho"))
        self.assertTrue(usuario_declina_informacao_campo("não tem"))
        self.assertTrue(usuario_declina_informacao_campo("sem fotos"))
        self.assertTrue(usuario_declina_informacao_campo("não tenho fotos"))
        self.assertFalse(usuario_declina_informacao_campo("poste 4521 na rua das flores"))


class CampoOpcionalDeclinioFluxoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Cidão",
            email="decl@test.local",
        )
        cat = CategoriaCatalogo.objects.create(
            nome="Zeladoria decl", slug="zel-decl", tipo_legado="zeladoria", ativo=True
        )
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Iluminação teste",
            schema_formulario=SCHEMA_ILUMINACAO,
            ativo=True,
            sla_horas=48,
        )

    def _sessao(self) -> SessaoChat:
        s = SessaoChat.objects.create(
            usuario=self.user,
            categoria_inicial="Zeladoria",
            servico_identificado=self.servico,
            dados_coletados={"tipo_falha": "lampada_queimada"},
        )
        set_meta(s, fase=FaseChat.PREENCHIMENTO)
        s.save()
        return s

    def test_declinio_pula_numero_poste_e_avanca(self):
        sessao = self._sessao()
        orch = LLMOrchestrator()
        turno = orch._estagio_slot_filling(
            sessao,
            texto_usuario="não tenho a informação",
            anexos_novos=0,
        )
        sessao.refresh_from_db()
        pulados = (sessao.dados_coletados or {}).get("_campos_pulados") or []
        self.assertIn("numero_poste", pulados)
        faltantes = _campos_faltantes(self.servico, sessao.dados_coletados or {}, sessao)
        self.assertNotIn("numero_poste", faltantes)
        self.assertEqual(faltantes[0], "localizacao")
        self.assertIn(turno.acao_ui, ("solicitar_localizacao", None))

    def test_registrar_pulado_manual_equivale(self):
        sessao = self._sessao()
        registrar_campo_pulado(sessao, "numero_poste")
        sessao.refresh_from_db()
        faltantes = _campos_faltantes(self.servico, sessao.dados_coletados or {}, sessao)
        self.assertEqual(faltantes, ["localizacao"])


SCHEMA_FOTO_OPCIONAL = {
    "type": "object",
    "properties": {
        "tipo_falha": {"type": "string", "title": "Tipo"},
        "localizacao": {
            "type": "string",
            "title": "Local",
            "x-ouvia-tipo-campo": "geolocation",
        },
        "f": {
            "type": "string",
            "title": "Foto do poste",
            "x-ouvia-tipo-campo": "image",
        },
    },
    "required": ["tipo_falha", "localizacao"],
    "$metadata": {
        "ordem_campos": ["tipo_falha", "localizacao", "f"],
        "exige_localizacao": True,
        "exige_foto": True,
    },
}


class FotoOpcionalExigeFotoMetadataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            cpf="39053344706",
            password="x",
            nome="Cidão Foto",
            email="foto@test.local",
        )
        cat = CategoriaCatalogo.objects.create(
            nome="Zeladoria foto", slug="zel-foto", tipo_legado="zeladoria", ativo=True
        )
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Iluminação foto opcional",
            schema_formulario=SCHEMA_FOTO_OPCIONAL,
            ativo=True,
            sla_horas=48,
        )

    def _sessao_com_local(self) -> SessaoChat:
        s = SessaoChat.objects.create(
            usuario=self.user,
            categoria_inicial="Zeladoria",
            servico_identificado=self.servico,
            dados_coletados={
                "tipo_falha": "lampada_queimada",
                "_localizacao": {
                    "latitude": -23.55,
                    "longitude": -46.18,
                    "endereco": "Rua Teste",
                },
            },
        )
        set_meta(s, fase=FaseChat.PREENCHIMENTO)
        s.save()
        return s

    def test_anexo_nao_obrigatorio_com_campo_imagem_opcional(self):
        sessao = self._sessao_com_local()
        self.assertFalse(_anexo_sessao_obrigatorio(sessao, self.servico))

    def test_sem_fotos_pula_e_liberar_revisao(self):
        sessao = self._sessao_com_local()
        orch = LLMOrchestrator()
        turno = orch._estagio_slot_filling(
            sessao,
            texto_usuario="sem fotos",
            anexos_novos=0,
        )
        sessao.refresh_from_db()
        pulados = (sessao.dados_coletados or {}).get("_campos_pulados") or []
        self.assertIn("f", pulados)
        self.assertTrue(_requisitos_revisao_ok(sessao))
        self.assertTrue(
            turno.ir_para_revisao or turno.acao_ui == "revisao_final" or MSG_REVISAO in (turno.resposta_cidadao or "")
        )

    def test_nao_tenho_em_foto_opcional_nao_repete_pergunta(self):
        sessao = self._sessao_com_local()
        dados = dict(sessao.dados_coletados or {})
        dados["numero_poste"] = "123"
        sessao.dados_coletados = dados
        sessao.save()
        orch = LLMOrchestrator()
        turno = orch._estagio_slot_filling(
            sessao,
            texto_usuario="não tenho",
            anexos_novos=0,
        )
        sessao.refresh_from_db()
        pulados = (sessao.dados_coletados or {}).get("_campos_pulados") or []
        self.assertIn("f", pulados)
        self.assertNotEqual((turno.resposta_cidadao or "").strip(), "Foto do poste")