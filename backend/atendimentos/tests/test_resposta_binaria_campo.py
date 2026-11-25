"""Respostas sim/não em campos binários ou opcionais tipo texto (evita loop no chat)."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from atendimentos.chat_estado import FaseChat, set_meta
from atendimentos.llm_orchestrator import (
    LLMOrchestrator,
    _campos_faltantes,
    _dados_negocio,
    _extrair_resposta_binaria_campo,
)
from atendimentos.models import SessaoChat
from catalogo.models import CategoriaCatalogo, ServicoCatalogo

User = get_user_model()

SCHEMA_BURACOS = {
    "type": "object",
    "properties": {
        "tipo_problema": {
            "type": "array",
            "title": "Tipo de Problema",
            "items": {"type": "string", "enum": ["buraco"]},
        },
        "tamanho_aproximado": {
            "type": "string",
            "title": "Tamanho",
            "enum": ["pequeno", "medio", "grande"],
        },
        "causa_risco": {
            "type": "string",
            "title": "Causa risco imediato aos pedestres ou veículos",
        },
    },
    "required": ["tipo_problema", "tamanho_aproximado"],
    "$metadata": {
        "ordem_campos": [
            "causa_risco",
            "tipo_problema",
            "tamanho_aproximado",
        ],
    },
}


class RespostaBinariaCampoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            cpf="52998224725",
            password="x",
            nome="Cid Teste",
            email="bin@test.local",
        )
        cat = CategoriaCatalogo.objects.create(
            nome="Zel", slug="zel-bin", tipo_legado="zeladoria", ativo=True
        )
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Buracos teste",
            schema_formulario=SCHEMA_BURACOS,
            ativo=True,
            sla_horas=48,
        )

    def test_sim_preenche_causa_risco_opcional_string(self):
        val = _extrair_resposta_binaria_campo(self.servico, "causa_risco", "sim")
        self.assertEqual(val, "sim")

    def test_obrigatorios_antes_opcionais_na_fila(self):
        falt = _campos_faltantes(self.servico, {}, None)
        self.assertEqual(falt[0], "tipo_problema")

    def test_turno_avanca_apos_sim_no_risco(self):
        sessao = SessaoChat.objects.create(
            usuario=self.user,
            categoria_inicial="Zeladoria",
            servico_identificado=self.servico,
            dados_coletados={},
        )
        set_meta(sessao, fase=FaseChat.PREENCHIMENTO)
        sessao.save()
        orch = LLMOrchestrator()
        turno = orch.processar_turno(sessao, texto_usuario="sim", anexos_novos=0)
        sessao.refresh_from_db()
        self.assertEqual(sessao.dados_coletados.get("causa_risco"), "sim")
        self.assertNotIn(
            "Causa risco imediato",
            (turno.resposta_cidadao or ""),
        )