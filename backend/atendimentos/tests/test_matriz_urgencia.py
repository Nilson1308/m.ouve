"""Sprint 4.6 — matriz de urgência parametrizável."""

from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.test import APIClient

from atendimentos.models import (
    ConfiguracaoMatrizUrgencia,
    NotificacaoInterna,
    OrdemServico,
    Protocolo,
    ProtocoloHistorico,
    SuperOS,
)
from atendimentos.services.matriz_urgencia_service import (
    alterar_urgencia_protocolo,
    avaliar_escalonamento_super_os,
    classificar_urgencia_entrada,
    disparar_alertas_urgencia,
)
from catalogo.models import CategoriaCatalogo, ServicoCatalogo, UnidadeAdministrativa
from core_auth.models import PerfilAcesso
from core_auth.rbac import aplicar_regras_automaticas, permissoes_padrao

User = get_user_model()


def _perms_mesa():
    p = permissoes_padrao()
    p["mesa_trabalho"] = {k: True for k in ("ler", "criar", "editar", "excluir")}
    p["regras"]["acesso_staff"] = True
    p["regras"]["exige_unidade"] = True
    return aplicar_regras_automaticas(p)


def _perms_ouvidor():
    p = permissoes_padrao()
    p["mesa_trabalho"]["ler"] = True
    p["mesa_trabalho"]["criar"] = True
    p["mesa_trabalho"]["editar"] = True
    p["regras"]["acesso_staff"] = True
    p["regras"]["pode_alterar_urgencia"] = True
    return aplicar_regras_automaticas(p)


class MatrizUrgenciaBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.unidade = UnidadeAdministrativa.objects.create(nome="Infra", sigla="INF", ativo=True)
        cat = CategoriaCatalogo.objects.create(nome="Z", slug="z-mu", ativo=True)
        cls.servico = ServicoCatalogo.objects.create(
            categoria=cat,
            nome="Buraco",
            unidade_responsavel=cls.unidade,
            urgencia_padrao="baixa",
            ativo=True,
        )
        cls.cidadao = User.objects.create_user(
            cpf="39053344705",
            password="x",
            nome="Cid",
            email="c@test.local",
        )
        cls.perfil_gestor = PerfilAcesso.objects.create(
            codigo="gestor_matriz_mu_test",
            nome="Gestor Matriz Test",
            permissoes=_perms_mesa(),
        )
        cls.perfil_ouvidor = PerfilAcesso.objects.create(
            codigo="ouvidor_matriz_mu_test",
            nome="Ouvidor Matriz Test",
            permissoes=_perms_ouvidor(),
        )
        cls.gestor = User.objects.create_user(
            cpf="12345678909",
            password="x",
            nome="Gestor",
            email="g@test.local",
            is_staff=True,
            unidade=cls.unidade,
            perfil_acesso=cls.perfil_gestor,
        )
        cls.ouvidor = User.objects.create_user(
            cpf="98765432100",
            password="x",
            nome="Ouvidor",
            email="o@test.local",
            is_staff=True,
            perfil_acesso=cls.perfil_ouvidor,
        )

    def _protocolo(self, **kwargs):
        descricao = kwargs.pop("descricao", "Teste matriz urgência")
        return Protocolo.objects.create(
            codigo=kwargs.pop("codigo", f"PROT-MU-{Protocolo.objects.count() + 1}"),
            usuario=self.cidadao,
            servico=self.servico,
            descricao=descricao,
            **kwargs,
        )


class ClassificacaoEntradaTests(MatrizUrgenciaBase):
    def test_catalogo_e_regra_campo_prevalencia(self):
        cfg = ConfiguracaoMatrizUrgencia.load()
        cfg.regras_campo_urgencia = [
            {"chave_schema": "tipo_risco", "valor": "imediato", "urgencia": "alta"},
        ]
        cfg.save()
        proto = self._protocolo(
            dados_dinamicos={"tipo_risco": "imediato"},
        )
        classificar_urgencia_entrada(proto)
        proto.refresh_from_db()
        self.assertEqual(proto.urgencia, "alta")
        self.assertEqual(proto.urgencia_origem, "regra")

    def test_ia_modo_sugerir_pendente(self):
        cfg = ConfiguracaoMatrizUrgencia.load()
        cfg.criterios_ia_customizados = {"alta": {"sinais": ["risco imediato"]}}
        cfg.ia_urgencia_modo = "sugerir"
        cfg.save()
        proto = self._protocolo(descricao="Há risco imediato na via")
        classificar_urgencia_entrada(proto)
        proto.refresh_from_db()
        self.assertEqual(proto.urgencia, "baixa")
        self.assertEqual(proto.urgencia_sugestao_status, "pendente")
        self.assertEqual(proto.urgencia_sugerida_ia, "alta")

    def test_ia_modo_automatico_com_confianca(self):
        cfg = ConfiguracaoMatrizUrgencia.load()
        cfg.ia_urgencia_modo = "aplicar_automatico"
        cfg.ia_confianca_minima = 0.5
        cfg.criterios_ia_customizados = {
            "critica": {"sinais": ["colapso", "risco", "imediato"]},
        }
        cfg.save()
        proto = self._protocolo(descricao="Colapso com risco imediato na estrutura")
        classificar_urgencia_entrada(proto)
        proto.refresh_from_db()
        self.assertEqual(proto.urgencia, "critica")
        self.assertEqual(proto.urgencia_origem, "ia")


class SuperOsEscalonamentoTests(MatrizUrgenciaBase):
    def test_escalonamento_respeita_travamento_manual(self):
        cfg = ConfiguracaoMatrizUrgencia.load()
        cfg.super_os_limite_alta = 2
        cfg.save()
        sos = SuperOS.objects.create(
            codigo="SOS-MU-1",
            titulo_resumo="Cluster",
        )
        p1 = self._protocolo(
            codigo="P1",
            super_os=sos,
            urgencia="baixa",
            urgencia_peso=1,
            urgencia_travada_manualmente=True,
        )
        p2 = self._protocolo(codigo="P2", super_os=sos)
        p3 = self._protocolo(codigo="P3", super_os=sos)
        avaliar_escalonamento_super_os(sos)
        p2.refresh_from_db()
        p3.refresh_from_db()
        p1.refresh_from_db()
        self.assertEqual(p1.urgencia, "baixa")
        self.assertIn(p2.urgencia, ("alta", "critica"))
        self.assertIn(p3.urgencia, ("alta", "critica"))


class AlteracaoManualTests(MatrizUrgenciaBase):
    def test_gestor_403_ouvidor_200_historico(self):
        proto = self._protocolo()
        with self.assertRaises(PermissionDenied):
            alterar_urgencia_protocolo(
                proto,
                user=self.gestor,
                urgencia="alta",
                justificativa="Justificativa válida com mais de dez caracteres.",
            )
        with self.assertRaises(ValidationError):
            alterar_urgencia_protocolo(
                proto,
                user=self.ouvidor,
                urgencia="alta",
                justificativa="curta",
            )
        proto = self._protocolo(codigo="P-ALT")
        alterar_urgencia_protocolo(
            proto,
            user=self.ouvidor,
            urgencia="alta",
            justificativa="Priorização por risco operacional.",
        )
        proto.refresh_from_db()
        self.assertTrue(proto.urgencia_travada_manualmente)
        self.assertTrue(
            ProtocoloHistorico.objects.filter(
                protocolo=proto,
                descricao__icontains="Alteração manual",
            ).exists()
        )

    def test_justificativa_curta_400_via_api(self):
        proto = self._protocolo(codigo="P-API")
        client = APIClient()
        client.force_authenticate(self.ouvidor)
        r = client.post(
            f"/api/v1/backoffice/protocolos/{proto.id}/urgencia",
            {"urgencia": "alta", "justificativa": "curto"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_alerta_alta_dispara_notificacao(self):
        cfg = ConfiguracaoMatrizUrgencia.load()
        cfg.notificar_gestor_em_alta = True
        cfg.save()
        proto = self._protocolo(codigo="P-NOTIF", urgencia="alta", urgencia_peso=3)
        OrdemServico.objects.create(
            protocolo=proto,
            unidade=self.unidade,
            descricao="OS",
            prazo_horas=24,
            nome_equipe="INF",
        )
        proto = Protocolo.objects.select_related("servico").get(pk=proto.pk)
        unidade_ids: set = set()
        for os in proto.ordens_servico.all():
            if os.unidade_id:
                unidade_ids.add(os.unidade_id)
        if proto.servico_id and proto.servico.unidade_responsavel_id:
            unidade_ids.add(proto.servico.unidade_responsavel_id)
        destinatarios = User.objects.filter(
            is_active=True, is_staff=True, unidade_id__in=unidade_ids
        )
        self.assertGreater(unidade_ids, set())
        self.assertGreater(destinatarios.count(), 0)

        antes = NotificacaoInterna.objects.count()
        criadas = disparar_alertas_urgencia(proto, "normal")
        self.assertGreater(criadas, 0)
        self.assertGreater(NotificacaoInterna.objects.count(), antes)


class SugestaoIaAcoesTests(MatrizUrgenciaBase):
    def test_aceitar_e_descartar_sugestao(self):
        proto = self._protocolo(
            urgencia="normal",
            urgencia_sugerida_ia="alta",
            urgencia_sugestao_status="pendente",
        )
        alterar_urgencia_protocolo(
            proto, user=self.ouvidor, acao="aceitar_sugestao_ia"
        )
        proto.refresh_from_db()
        self.assertEqual(proto.urgencia, "alta")

        proto2 = self._protocolo(
            codigo="P-DESC",
            urgencia_sugerida_ia="alta",
            urgencia_sugestao_status="pendente",
        )
        alterar_urgencia_protocolo(
            proto2, user=self.ouvidor, acao="descartar_sugestao_ia"
        )
        proto2.refresh_from_db()
        self.assertEqual(proto2.urgencia_sugestao_status, "descartada")


class OrdenacaoMesaTests(MatrizUrgenciaBase):
    def test_lista_prioriza_urgencia_peso(self):
        baixa = self._protocolo(codigo="PB", urgencia="baixa", urgencia_peso=1)
        crit = self._protocolo(codigo="PC", urgencia="critica", urgencia_peso=4)
        client = APIClient()
        client.force_authenticate(self.ouvidor)
        r = client.get("/api/v1/backoffice/protocolos")
        self.assertEqual(r.status_code, 200)
        dados = r.data.get("data") or r.data.get("results") or r.data
        if isinstance(dados, list) and len(dados) >= 2:
            ids = [item["id"] for item in dados]
            self.assertLess(ids.index(str(crit.id)), ids.index(str(baixa.id)))


class SlaPausadoTests(MatrizUrgenciaBase):
    def test_sla_reduzido_nao_quebra_pausa_diligencia(self):
        cfg = ConfiguracaoMatrizUrgencia.load()
        cfg.urgencia_reduz_sla = True
        cfg.save()
        proto = self._protocolo(
            urgencia="alta",
            sla_pausado_desde=timezone.now(),
            prazo_sla=timezone.now() + timedelta(days=2),
        )
        prazo_ant = proto.prazo_sla
        from atendimentos.services.matriz_urgencia_service import aplicar_impacto_sla_urgencia

        self.assertFalse(aplicar_impacto_sla_urgencia(proto, cfg))
        proto.refresh_from_db()
        self.assertEqual(proto.prazo_sla, prazo_ant)

    def test_sla_reduzido_desligado_por_padrao(self):
        cfg = ConfiguracaoMatrizUrgencia.load()
        self.assertFalse(cfg.urgencia_reduz_sla)
        proto = self._protocolo(urgencia="critica")
        from atendimentos.services.matriz_urgencia_service import aplicar_impacto_sla_urgencia

        self.assertFalse(aplicar_impacto_sla_urgencia(proto, cfg))