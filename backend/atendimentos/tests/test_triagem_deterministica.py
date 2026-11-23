"""Motor de triagem determinística (Onda 3)."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from atendimentos.models import Protocolo, ProtocoloHistorico
from atendimentos.services.triagem_service import (
    executar_triagem_protocolo,
    montar_triagem_sugerida,
)
from catalogo.models import (
    CategoriaCatalogo,
    MatrizRoteamentoTematico,
    ServicoCatalogo,
    UnidadeAdministrativa,
)
from core_auth.models import PerfilAcesso
from core_auth.rbac import aplicar_regras_automaticas, permissoes_padrao

User = get_user_model()


def _perfil_mesa():
    base = permissoes_padrao()
    base["mesa_trabalho"] = {"ler": True, "criar": True, "editar": True, "excluir": False}
    return aplicar_regras_automaticas(base)


class TriagemDeterministicaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = CategoriaCatalogo.objects.create(
            nome="Cat Triagem", slug="cat-triagem", ativo=True
        )
        cls.u_saude = UnidadeAdministrativa.objects.create(
            nome="Secretaria de Saúde", sigla="SMS", ativo=True
        )
        cls.u_educacao = UnidadeAdministrativa.objects.create(
            nome="Secretaria de Educação", sigla="SME", ativo=True
        )
        cls.cidadao = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Cidadão",
            email="cidadao.triagem@test.local",
        )
        cls.schema_lookup = {
            "type": "object",
            "properties": {
                "unidade_destino": {
                    "type": "string",
                    "format": "uuid",
                    "x-ouvia-datasource": "unidades_administrativas",
                },
                "categoria": {"type": "string"},
            },
        }
        cls.servico_encaminha = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Ouvidoria encaminha",
            unidade_responsavel=cls.u_saude,
            ativo=True,
            fluxo_tramitacao=ServicoCatalogo.FluxoTramitacao.OUVIDORIA_ENCAMINHA,
            schema_formulario=cls.schema_lookup,
        )
        cls.servico_direto = ServicoCatalogo.objects.create(
            categoria=cls.categoria,
            nome="Direto secretaria",
            unidade_responsavel=cls.u_saude,
            ativo=True,
            fluxo_tramitacao=ServicoCatalogo.FluxoTramitacao.DIRETO_SECRETARIA,
            schema_formulario=cls.schema_lookup,
        )
        MatrizRoteamentoTematico.objects.create(
            servico=cls.servico_encaminha,
            chave_schema="categoria",
            valor_condicao="saude",
            unidade_sugerida=cls.u_saude,
            ativo=True,
        )
        MatrizRoteamentoTematico.objects.create(
            servico=cls.servico_encaminha,
            chave_schema="categoria",
            valor_condicao="educacao",
            unidade_sugerida=cls.u_educacao,
            ativo=True,
        )

    def _protocolo(self, servico, dados):
        return Protocolo.objects.create(
            codigo=Protocolo.gerar_codigo(),
            usuario=self.cidadao,
            servico=servico,
            dados_dinamicos=dados,
            descricao="Teste triagem",
            status=Protocolo.Status.EM_ANALISE,
        )

    def test_apenas_matriz(self):
        p = self._protocolo(self.servico_encaminha, {"categoria": "educacao"})
        payload = montar_triagem_sugerida(p)
        self.assertEqual(len(payload["unidades_sugeridas"]), 1)
        self.assertEqual(payload["unidades_sugeridas"][0]["id"], str(self.u_educacao.id))
        self.assertEqual(payload["unidades_sugeridas"][0]["fonte"], "matriz_eixo")
        self.assertEqual(payload["versao_motor"], "deterministico_v1")

    def test_apenas_lookup(self):
        p = self._protocolo(
            self.servico_encaminha,
            {"unidade_destino": str(self.u_educacao.id)},
        )
        payload = executar_triagem_protocolo(p)
        self.assertEqual(len(payload["unidades_sugeridas"]), 1)
        self.assertEqual(payload["unidades_sugeridas"][0]["confianca"], 1.0)
        self.assertEqual(payload["unidades_sugeridas"][0]["fonte"], "lookup_cidadao")

    def test_lookup_e_matriz_mesma_unidade_sem_duplicar(self):
        p = self._protocolo(
            self.servico_encaminha,
            {
                "unidade_destino": str(self.u_saude.id),
                "categoria": "saude",
            },
        )
        payload = executar_triagem_protocolo(p)
        ids = [u["id"] for u in payload["unidades_sugeridas"]]
        self.assertEqual(len(ids), 1)
        self.assertEqual(ids[0], str(self.u_saude.id))
        self.assertEqual(payload["unidades_sugeridas"][0]["confianca"], 1.0)

    def test_direto_secretaria_nao_gera_sugestao(self):
        p = self._protocolo(
            self.servico_direto,
            {"categoria": "saude", "unidade_destino": str(self.u_saude.id)},
        )
        payload = executar_triagem_protocolo(p)
        self.assertEqual(payload, {})
        p.refresh_from_db()
        self.assertEqual(p.triagem_sugerida, {})

    def test_despacho_registra_auditoria_triagem(self):
        perfil = PerfilAcesso.objects.create(
            codigo="mesa_triagem",
            nome="Mesa",
            permissoes=_perfil_mesa(),
            ativo=True,
        )
        ouvidor = User.objects.create_user(
            cpf="15350946056",
            password="x",
            nome="Ouvidor",
            email="ouvidor.triagem@test.local",
            perfil_acesso=perfil,
        )
        p = self._protocolo(self.servico_encaminha, {"categoria": "saude"})
        executar_triagem_protocolo(p)
        client = APIClient()
        client.force_authenticate(user=ouvidor)
        resp = client.post(
            f"/api/v1/backoffice/protocolos/{p.id}/despachar",
            {
                "ordens": [
                    {
                        "unidade_id": str(self.u_saude.id),
                        "instrucao": "Atender",
                        "prazo_horas": 48,
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        hist = ProtocoloHistorico.objects.filter(protocolo=p).order_by("-registrado_em").first()
        self.assertIn("Auditoria de triagem", hist.descricao)
        self.assertIn("confirmou sugestão", hist.descricao)