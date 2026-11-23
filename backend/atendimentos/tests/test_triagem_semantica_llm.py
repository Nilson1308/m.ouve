"""Triagem semântica (Onda 4) — LLM, Celery e merge com triagem determinística."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from catalogo.models import (
    CategoriaCatalogo,
    MatrizRoteamentoTematico,
    ServicoCatalogo,
    UnidadeAdministrativa,
)
from atendimentos.models import Protocolo
from atendimentos.services.triagem_service import (
    FONTE_LLM,
    FONTE_MATRIZ,
    executar_triagem_protocolo,
    executar_triagem_semantica_llm,
    merge_triagem_com_llm,
    _filtrar_sugestoes_llm,
)

User = get_user_model()


class TriagemSemanticaMergeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u_saude = UnidadeAdministrativa.objects.create(
            nome="Secretaria de Saúde", sigla="SMS", ativo=True
        )

    def test_merge_matriz_prevalece_fonte_mas_usa_maior_confianca(self):
        base = {
            "unidades_sugeridas": [
                {
                    "id": str(self.u_saude.id),
                    "nome": self.u_saude.nome,
                    "confianca": 0.85,
                    "fonte": FONTE_MATRIZ,
                    "motivo": "Regra categoria=saude",
                }
            ],
            "versao_motor": "deterministico_v1",
        }
        llm = [
            {
                "id": str(self.u_saude.id),
                "nome": self.u_saude.nome,
                "confianca": 0.9,
                "fonte": FONTE_LLM,
                "motivo": "Relato indica demanda em saúde",
            }
        ]
        merged = merge_triagem_com_llm(base, llm, resumo_motivo="Saúde", versao_modelo="test-model")
        item = merged["unidades_sugeridas"][0]
        self.assertEqual(item["fonte"], FONTE_MATRIZ)
        self.assertEqual(item["confianca"], 0.9)
        self.assertIn("IA:", item["motivo"])

    def test_filtra_uuid_inexistente_e_confianca_baixa(self):
        mapa = {str(self.u_saude.id): self.u_saude}
        raw = {
            "resumo_motivo": "Teste",
            "unidades": [
                {
                    "id": "00000000-0000-4000-8000-000000000099",
                    "confianca": 0.99,
                    "motivo": "Alucinado",
                },
                {"id": str(self.u_saude.id), "confianca": 0.3, "motivo": "Baixo"},
                {"id": str(self.u_saude.id), "confianca": 0.78, "motivo": "OK"},
            ],
        }
        validas, resumo = _filtrar_sugestoes_llm(raw, mapa)
        self.assertEqual(len(validas), 1)
        self.assertEqual(validas[0]["confianca"], 0.78)
        self.assertEqual(resumo, "Teste")


class TriagemSemanticaCeleryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = CategoriaCatalogo.objects.create(
            nome="Cat LLM", slug="cat-llm", ativo=True
        )
        cls.u_saude = UnidadeAdministrativa.objects.create(
            nome="SMS", sigla="SMS", ativo=True
        )
        cls.u_educ = UnidadeAdministrativa.objects.create(
            nome="SME", sigla="SME", ativo=True
        )
        cls.cidadao = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Cidadão",
            email="llm@test.local",
        )
        cls.servico_ia = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Com IA",
            unidade_responsavel=cls.u_saude,
            ativo=True,
            fluxo_tramitacao=ServicoCatalogo.FluxoTramitacao.OUVIDORIA_ENCAMINHA,
            triagem_ia_ativa=True,
            schema_formulario={"properties": {"categoria": {"type": "string"}}},
        )
        cls.servico_sem_ia = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Sem IA",
            unidade_responsavel=cls.u_saude,
            ativo=True,
            fluxo_tramitacao=ServicoCatalogo.FluxoTramitacao.OUVIDORIA_ENCAMINHA,
            triagem_ia_ativa=False,
        )
        cls.servico_direto = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Direto",
            unidade_responsavel=cls.u_saude,
            ativo=True,
            fluxo_tramitacao=ServicoCatalogo.FluxoTramitacao.DIRETO_SECRETARIA,
            triagem_ia_ativa=True,
        )
        MatrizRoteamentoTematico.objects.create(
            servico=cls.servico_ia,
            chave_schema="categoria",
            valor_condicao="saude",
            unidade_sugerida=cls.u_saude,
            ativo=True,
        )

    def _protocolo(self, servico):
        return Protocolo.objects.create(
            codigo=Protocolo.gerar_codigo(),
            usuario=self.cidadao,
            servico=servico,
            dados_dinamicos={"categoria": "saude"},
            descricao="Relato de problema de saúde",
            status=Protocolo.Status.EM_ANALISE,
        )

    @patch("atendimentos.tasks.executar_triagem_semantica_task.delay")
    def test_enfileira_task_quando_triagem_ia_ativa(self, delay_mock):
        p = self._protocolo(self.servico_ia)
        with self.captureOnCommitCallbacks(execute=True):
            executar_triagem_protocolo(p)
        delay_mock.assert_called_once_with(str(p.id))

    @patch("atendimentos.tasks.executar_triagem_semantica_task.delay")
    def test_nao_enfileira_sem_triagem_ia(self, delay_mock):
        p = self._protocolo(self.servico_sem_ia)
        with self.captureOnCommitCallbacks(execute=True):
            executar_triagem_protocolo(p)
        delay_mock.assert_not_called()

    @patch("atendimentos.tasks.executar_triagem_semantica_task.delay")
    def test_nao_enfileira_direto_secretaria(self, delay_mock):
        p = self._protocolo(self.servico_direto)
        with self.captureOnCommitCallbacks(execute=True):
            executar_triagem_protocolo(p)
        delay_mock.assert_not_called()

    @override_settings(LLM_CHAT_API_KEY="test-key")
    @patch("atendimentos.services.triagem_service._chamar_llm_triagem_semantica")
    def test_merge_llm_com_matriz_sem_duplicar(self, mock_llm):
        mock_llm.return_value = {
            "unidades": [
                {
                    "id": str(self.u_educ.id),
                    "confianca": 0.78,
                    "motivo": "Educação complementar",
                }
            ],
            "resumo_motivo": "Sugestão mista",
        }
        p = self._protocolo(self.servico_ia)
        executar_triagem_protocolo(p)
        p.refresh_from_db()
        base = dict(p.triagem_sugerida)
        resultado = executar_triagem_semantica_llm(p.id)
        self.assertIsNotNone(resultado)
        ids = {u["id"] for u in resultado["unidades_sugeridas"]}
        self.assertIn(str(self.u_saude.id), ids)
        self.assertIn(str(self.u_educ.id), ids)
        self.assertEqual(resultado["versao_motor"], "hibrido_llm_v1")
        saude = next(u for u in resultado["unidades_sugeridas"] if u["id"] == str(self.u_saude.id))
        self.assertEqual(saude["fonte"], FONTE_MATRIZ)
        self.assertGreaterEqual(saude["confianca"], 0.85)

    @override_settings(LLM_CHAT_API_KEY="test-key")
    @patch(
        "atendimentos.services.triagem_service._chamar_llm_triagem_semantica",
        side_effect=RuntimeError("LLM off"),
    )
    def test_fallback_preserva_deterministico(self, _mock_llm):
        p = self._protocolo(self.servico_ia)
        executar_triagem_protocolo(p)
        p.refresh_from_db()
        antes = dict(p.triagem_sugerida)
        executar_triagem_semantica_llm(p.id)
        p.refresh_from_db()
        self.assertEqual(p.triagem_sugerida, antes)

    @override_settings(LLM_CHAT_API_KEY="")
    def test_sem_api_key_nao_sobrescreve(self):
        p = self._protocolo(self.servico_ia)
        executar_triagem_protocolo(p)
        p.refresh_from_db()
        antes = dict(p.triagem_sugerida)
        executar_triagem_semantica_llm(p.id)
        p.refresh_from_db()
        self.assertEqual(p.triagem_sugerida, antes)