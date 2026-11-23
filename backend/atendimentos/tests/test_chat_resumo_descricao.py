"""Descrição e campos exibidos no detalhe do protocolo (PWA)."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from atendimentos.chat_resumo import (
    descricao_exibicao_cidadao,
    limpar_descricao_legada,
    montar_campos_protocolo_publico,
)
from atendimentos.models import Protocolo
from catalogo.models import CategoriaCatalogo, ServicoCatalogo

User = get_user_model()

TEXTO_LONGO = (
    "estive na UPA de Jundiapeba para um atendimento com urgência e esperei mais de 3 horas"
)

BLOCO_ANTIGO = f"""Serviço: Ouvidoria
Relato do cidadão:
• quero fazer uma reclamação
• ✓ O que deseja manifestar?: Reclamação
• {TEXTO_LONGO}
Dados da solicitação:
• O que deseja manifestar?: Reclamação
• Descreva sua manifestação: {TEXTO_LONGO}"""


class ChatResumoDescricaoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cat = CategoriaCatalogo.objects.create(nome="Ouv", slug="ouv-desc", ativo=True)
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Ouvidoria",
            ativo=True,
            schema_formulario={
                "type": "object",
                "required": ["o", "q", "d"],
                "properties": {
                    "o": {"type": "string", "title": "O que deseja manifestar"},
                    "q": {"type": "string", "title": "Qual área/setor"},
                    "d": {"type": "string", "title": "Descreva sua manifestação", "format": "textarea"},
                },
            },
        )
        cls.cidadao = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Teste",
            email="desc@test.local",
        )

    def test_limpar_descricao_legada_remove_redundancia(self):
        limpa = limpar_descricao_legada(BLOCO_ANTIGO)
        self.assertIn("UPA de Jundiapeba", limpa)
        self.assertNotIn("Dados da solicitação", limpa)
        self.assertNotIn("✓", limpa)

    def test_campos_com_rotulos_do_schema(self):
        campos = montar_campos_protocolo_publico(
            self.servico,
            {"o": "Reclamação", "q": "Saúde", "d": TEXTO_LONGO, "bairro": "Centro"},
        )
        rotulos = {c["rotulo"] for c in campos}
        self.assertIn("O que deseja manifestar", rotulos)
        self.assertIn("Qual área/setor", rotulos)
        chaves = {c["chave"] for c in campos}
        self.assertNotIn("d", chaves)

    def test_descricao_exibicao_prioriza_campo_narrativa(self):
        protocolo = Protocolo.objects.create(
            codigo="PROT-DESC-1",
            usuario=self.cidadao,
            servico=self.servico,
            descricao=BLOCO_ANTIGO,
            dados_dinamicos={"o": "Reclamação", "q": "Saúde", "d": TEXTO_LONGO},
            status=Protocolo.Status.EM_ANALISE,
        )
        self.assertEqual(descricao_exibicao_cidadao(protocolo), TEXTO_LONGO)