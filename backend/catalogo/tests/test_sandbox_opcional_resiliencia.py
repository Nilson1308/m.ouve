"""Sandbox do catálogo — round-trip de _campos_pulados e declínio em opcionais."""

from django.test import TestCase

from catalogo.models import CategoriaCatalogo, ServicoCatalogo
from catalogo.sandbox_service import executar_sandbox_servico_catalogo

SCHEMA_ILUMINACAO_SANDBOX = {
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
        "foto": {
            "type": "string",
            "title": "Foto do poste",
            "x-ouvia-tipo-campo": "image",
        },
    },
    "required": ["tipo_falha", "localizacao"],
    "$metadata": {
        "ordem_campos": ["tipo_falha", "numero_poste", "localizacao", "foto"],
        "exige_localizacao": True,
    },
}


class SandboxOpcionalResilienciaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cat = CategoriaCatalogo.objects.create(
            nome="Zel Sandbox", slug="zel-sandbox-opt", tipo_legado="zeladoria", ativo=True
        )
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Iluminação sandbox",
            schema_formulario=SCHEMA_ILUMINACAO_SANDBOX,
            ativo=True,
            sla_horas=48,
        )

    def _rodar(self, **kwargs):
        return executar_sandbox_servico_catalogo(self.servico, **kwargs)

    def test_declinio_numero_poste_nao_repete_campo(self):
        dados = {"tipo_falha": "Lâmpada acesa durante o dia"}
        r1 = self._rodar(
            mensagem="",
            dados_parciais=dados,
            localizacao_ok=True,
            localizacao={"latitude": -23.5, "longitude": -46.6, "endereco": "Rua teste"},
        )
        dados = dict(r1["dados_parciais"])
        self.assertIn("_localizacao", dados)

        r2 = self._rodar(
            mensagem="não sei",
            dados_parciais=dados,
            localizacao_ok=True,
            localizacao=dados.get("_localizacao"),
            historico=r1.get("historico_sugerido"),
        )
        pulados = r2["dados_parciais"].get("_campos_pulados") or []
        self.assertIn("numero_poste", pulados)
        self.assertNotIn("número do poste", (r2.get("resposta_cidadao") or "").lower())

        r3 = self._rodar(
            mensagem="não sei",
            dados_parciais=r2["dados_parciais"],
            localizacao_ok=True,
            localizacao=r2["dados_parciais"].get("_localizacao"),
            historico=r2.get("historico_sugerido"),
        )
        pulados3 = r3["dados_parciais"].get("_campos_pulados") or []
        self.assertIn("numero_poste", pulados3)
        resposta = (r3.get("resposta_cidadao") or "").lower()
        self.assertNotIn("número do poste", resposta)

    def test_declinio_foto_opcional_vai_para_revisao(self):
        schema = SCHEMA_ILUMINACAO_SANDBOX
        dados = {
            "tipo_falha": "queimada",
            "_campos_pulados": ["numero_poste"],
            "_localizacao": {
                "latitude": -23.5,
                "longitude": -46.6,
                "endereco": "Rua A",
            },
        }
        ultimo = self._rodar(
            mensagem="não tenho",
            dados_parciais=dados,
            localizacao_ok=True,
            localizacao=dados["_localizacao"],
        )
        pulados = ultimo["dados_parciais"].get("_campos_pulados") or []
        self.assertIn("foto", pulados)
        self.assertTrue(
            ultimo.get("ir_para_revisao")
            or ultimo.get("acao_ui") == "revisao_final"
            or "resumo" in (ultimo.get("resposta_cidadao") or "").lower()
        )

    def test_stress_declinio_opcois_em_sequencia(self):
        """Cinco respostas de declínio não devem reiniciar campos já pulados."""
        dados: dict = {"tipo_falha": "oscilando"}
        historico: list = []
        frases = ["não sei", "sem informação", "não sei", "não tenho", "pular"]
        for frase in frases:
            out = self._rodar(
                mensagem=frase,
                dados_parciais=dados,
                localizacao_ok=True,
                localizacao={"latitude": -23.5, "longitude": -46.6, "endereco": "X"},
                historico=historico,
            )
            dados = dict(out["dados_parciais"])
            historico = out.get("historico_sugerido") or historico
        pulados = dados.get("_campos_pulados") or []
        self.assertGreaterEqual(len(pulados), 1)
        self.assertIn("numero_poste", pulados)