"""
Fixture de triagem de urgência (sugestão IA pendente) para validação E2E no backoffice.

Uso (staging / dev, com .env do backend):

  python manage.py seed_triagem_urgencia_demo --listar
  python manage.py seed_triagem_urgencia_demo --marcar PROT-2026-001
  python manage.py seed_triagem_urgencia_demo --criar
  python manage.py seed_triagem_urgencia_demo --criar --usar-classificador
  python manage.py seed_triagem_urgencia_demo --criar --dry-run
"""

from __future__ import annotations

import uuid
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from atendimentos.models import ConfiguracaoMatrizUrgencia, Protocolo
from atendimentos.services.matriz_urgencia_service import classificar_urgencia_entrada
from atendimentos.urgencia_constants import normalizar_nivel, peso_nivel
from catalogo.models import ServicoCatalogo
from django.contrib.auth import get_user_model

User = get_user_model()

DESCRICAO_DEMO = (
    "Relato demonstrativo para triagem: há risco imediato na via e falta de sinalização. "
    "Solicitação gerada pelo comando seed_triagem_urgencia_demo."
)
MOTIVO_PADRAO = "Sinais configurados na matriz: risco imediato (demonstração)."


class Command(BaseCommand):
    help = (
        "Lista, marca ou cria protocolo com urgencia_sugestao_status=pendente "
        "para testar Mesa, filtros e detalhe 360º."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--listar",
            action="store_true",
            help="Lista protocolos com sugestão de urgência pendente.",
        )
        parser.add_argument(
            "--marcar",
            metavar="CODIGO",
            help="Marca um protocolo existente com sugestão pendente (sem alterar urgência atual).",
        )
        parser.add_argument(
            "--criar",
            action="store_true",
            help="Cria um protocolo novo com sugestão pendente.",
        )
        parser.add_argument(
            "--sugerida",
            default="critica",
            choices=("alta", "critica"),
            help="Nível sugerido pela IA (modo --marcar ou carimbo direto).",
        )
        parser.add_argument(
            "--confianca",
            type=float,
            default=0.88,
            help="Confiança 0–1 exibida no detalhe (modo carimbo).",
        )
        parser.add_argument(
            "--motivo",
            default=MOTIVO_PADRAO,
            help="Texto exibido como motivo da sugestão.",
        )
        parser.add_argument(
            "--usar-classificador",
            action="store_true",
            help="Chama classificar_urgencia_entrada (heurística da matriz) em vez de carimbar campos.",
        )
        parser.add_argument(
            "--ajustar-matriz-demo",
            action="store_true",
            help="Ativa IA em modo sugerir e critérios de demo (somente com --criar --usar-classificador).",
        )
        parser.add_argument(
            "--servico-id",
            default="",
            help="UUID do serviço do catálogo (opcional; padrão: primeiro serviço ativo).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Não grava alterações.",
        )

    def handle(self, *args, **options):
        if options["listar"]:
            self._listar()
            return
        if options["marcar"]:
            self._marcar(options)
            return
        if options["criar"]:
            self._criar(options)
            return
        raise CommandError("Informe --listar, --marcar CODIGO ou --criar.")

    def _listar(self):
        qs = (
            Protocolo.objects.filter(
                urgencia_sugestao_status=Protocolo.UrgenciaSugestaoStatus.PENDENTE
            )
            .select_related("servico")
            .order_by("-data_criacao")[:25]
        )
        if not qs.exists():
            self.stdout.write("Nenhum protocolo com sugestão de urgência pendente.")
            return
        self.stdout.write(self.style.SUCCESS(f"{qs.count()} protocolo(s) com revisão pendente:\n"))
        for p in qs:
            sug = p.urgencia_sugerida_ia or "—"
            self.stdout.write(
                f"  • {p.codigo}  urgência={p.urgencia}  sugerida={sug}  "
                f"serviço={getattr(p.servico, 'nome', '—')}"
            )
        self.stdout.write(
            "\nFiltro Mesa/Setorial: apenas_sugestao_urgencia_ia=true"
        )
        self.stdout.write("Detalhe: /backoffice/protocolo/<código>")

    @transaction.atomic
    def _marcar(self, options):
        codigo = (options["marcar"] or "").strip()
        if not codigo:
            raise CommandError("Código do protocolo vazio.")
        try:
            proto = Protocolo.objects.select_for_update().get(codigo=codigo)
        except Protocolo.DoesNotExist as exc:
            raise CommandError(f"Protocolo {codigo} não encontrado.") from exc

        sugerida = normalizar_nivel(options["sugerida"], padrao="alta")
        if peso_nivel(sugerida) <= peso_nivel(proto.urgencia):
            self.stdout.write(
                self.style.WARNING(
                    f"Urgência atual ({proto.urgencia}) já é >= sugerida ({sugerida}). "
                    "A sugestão ainda será marcada como pendente para E2E."
                )
            )

        if options["dry_run"]:
            self.stdout.write(f"[dry-run] Marcaria {codigo} → sugerida={sugerida}")
            return

        proto.urgencia_sugerida_ia = sugerida
        proto.urgencia_motivo_ia = (options["motivo"] or MOTIVO_PADRAO).strip()
        proto.urgencia_confianca_ia = float(options["confianca"])
        proto.urgencia_sugestao_status = Protocolo.UrgenciaSugestaoStatus.PENDENTE
        proto.save(
            update_fields=[
                "urgencia_sugerida_ia",
                "urgencia_motivo_ia",
                "urgencia_confianca_ia",
                "urgencia_sugestao_status",
                "data_atualizacao",
            ]
        )
        self._imprimir_sucesso(proto)

    @transaction.atomic
    def _criar(self, options):
        servico = self._resolver_servico(options["servico_id"])
        usuario = self._resolver_usuario_cidadao()

        # Protocolo.codigo: max_length=20
        codigo = f"P-TRI-{datetime.now().strftime('%y%m%d')}{uuid.uuid4().hex[:4]}"
        while Protocolo.objects.filter(codigo=codigo).exists():
            codigo = f"P-TRI-{uuid.uuid4().hex[:12]}"
        if len(codigo) > 20:
            codigo = f"P-TRI-{uuid.uuid4().hex[:12]}"[:20]

        if options["ajustar_matriz_demo"] and options["usar_classificador"]:
            self._ajustar_matriz_demo(options["dry_run"])

        if options["dry_run"]:
            self.stdout.write(
                f"[dry-run] Criaria {codigo} (serviço={servico.nome}, classificador="
                f"{options['usar_classificador']})"
            )
            return

        proto = Protocolo.objects.create(
            codigo=codigo,
            usuario=usuario,
            servico=servico,
            descricao=DESCRICAO_DEMO,
            status=Protocolo.Status.EM_ANALISE,
            endereco_texto="Demonstração — triagem de urgência",
            urgencia=normalizar_nivel(getattr(servico, "urgencia_padrao", None), padrao="baixa"),
            urgencia_peso=peso_nivel(
                normalizar_nivel(getattr(servico, "urgencia_padrao", None), padrao="baixa")
            ),
            urgencia_origem=Protocolo.UrgenciaOrigem.CATALOGO,
        )

        if options["usar_classificador"]:
            classificar_urgencia_entrada(proto)
            proto.refresh_from_db()
            if proto.urgencia_sugestao_status != Protocolo.UrgenciaSugestaoStatus.PENDENTE:
                self.stdout.write(
                    self.style.WARNING(
                        "Classificador não gerou sugestão pendente "
                        "(verifique matriz: IA ativa, modo sugerir, sinais no relato). "
                        "Aplicando carimbo manual."
                    )
                )
                self._carimbar(proto, options)
        else:
            self._carimbar(proto, options)

        proto.refresh_from_db()
        self._imprimir_sucesso(proto)

    def _carimbar(self, proto: Protocolo, options):
        sugerida = normalizar_nivel(options["sugerida"], padrao="critica")
        proto.urgencia_sugerida_ia = sugerida
        proto.urgencia_motivo_ia = (options["motivo"] or MOTIVO_PADRAO).strip()
        proto.urgencia_confianca_ia = float(options["confianca"])
        proto.urgencia_sugestao_status = Protocolo.UrgenciaSugestaoStatus.PENDENTE
        proto.save(
            update_fields=[
                "urgencia_sugerida_ia",
                "urgencia_motivo_ia",
                "urgencia_confianca_ia",
                "urgencia_sugestao_status",
                "data_atualizacao",
            ]
        )

    def _ajustar_matriz_demo(self, dry: bool):
        cfg = ConfiguracaoMatrizUrgencia.load()
        if dry:
            self.stdout.write("[dry-run] Ajustaria matriz: IA ativa, modo sugerir, sinais demo.")
            return
        cfg.matriz_ativa = True
        cfg.ia_urgencia_ativa = True
        cfg.ia_urgencia_modo = "sugerir"
        crit = dict(cfg.criterios_ia_customizados or {})
        alta = dict(crit.get("alta") or {})
        sinais = list(alta.get("sinais") or alta.get("criterios") or [])
        for termo in ("risco imediato", "falta de sinalização"):
            if termo not in sinais:
                sinais.append(termo)
        alta["sinais"] = sinais
        crit["alta"] = alta
        critica = dict(crit.get("critica") or {})
        sinais_c = list(critica.get("sinais") or critica.get("criterios") or [])
        if "risco imediato" not in sinais_c:
            sinais_c.append("risco imediato")
        critica["sinais"] = sinais_c
        crit["critica"] = critica
        cfg.criterios_ia_customizados = crit
        cfg.save()
        self.stdout.write(self.style.NOTICE("Matriz ajustada para demonstração (modo sugerir + sinais)."))

    def _resolver_servico(self, servico_id: str) -> ServicoCatalogo:
        if servico_id:
            try:
                return ServicoCatalogo.objects.get(pk=servico_id, ativo=True)
            except ServicoCatalogo.DoesNotExist as exc:
                raise CommandError(f"Serviço {servico_id} não encontrado ou inativo.") from exc
        srv = ServicoCatalogo.objects.filter(ativo=True).order_by("nome").first()
        if not srv:
            raise CommandError("Nenhum serviço ativo no catálogo.")
        return srv

    def _resolver_usuario_cidadao(self):
        proto = Protocolo.objects.select_related("usuario").order_by("-data_criacao").first()
        if proto and proto.usuario_id:
            return proto.usuario
        user = User.objects.filter(is_active=True, is_staff=False).order_by("id").first()
        if user:
            return user
        raise CommandError(
            "Nenhum cidadão no banco. Crie um protocolo real ou um usuário cidadão antes."
        )

    def _imprimir_sucesso(self, proto: Protocolo):
        link = f"/backoffice/protocolo/{proto.codigo}"
        self.stdout.write(self.style.SUCCESS("\nProtocolo pronto para triagem E2E:\n"))
        self.stdout.write(f"  Código:     {proto.codigo}")
        self.stdout.write(f"  ID:         {proto.id}")
        self.stdout.write(f"  Urgência:   {proto.urgencia}")
        self.stdout.write(f"  Sugerida:   {proto.urgencia_sugerida_ia}")
        self.stdout.write(f"  Status IA:  {proto.urgencia_sugestao_status}")
        conf = proto.urgencia_confianca_ia
        if conf is not None:
            self.stdout.write(f"  Confiança:  {conf:.0%}")
        motivo = (proto.urgencia_motivo_ia or "").strip()
        if len(motivo) > 120:
            motivo = motivo[:120] + "…"
        self.stdout.write(f"  Motivo:     {motivo or '—'}")
        self.stdout.write(f"\n  Mesa:       filtro “Triagem de urgência (revisão pendente)”")
        self.stdout.write(f"  Detalhe:    {link}")
        self.stdout.write(
            f"\n  API teste (ouvidor): POST /api/v1/backoffice/protocolos/{proto.id}/urgencia"
        )
        self.stdout.write('    {"acao":"aceitar_sugestao_ia"}  ou  {"acao":"descartar_sugestao_ia"}')
        self.stdout.write(
            f"  Criado em:  {timezone.localtime(proto.data_criacao).strftime('%Y-%m-%d %H:%M')}"
        )