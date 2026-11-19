"""
Cenários de demonstração para a Matriz de Qualidade (várias secretarias no scatter).

Uso: python manage.py simular_matriz_qualidade_demo
"""

from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from atendimentos.models import Protocolo
from catalogo.models import ServicoCatalogo, UnidadeAdministrativa


class Command(BaseCommand):
    help = "Resolve protocolos de demo com notas e SLA variados para o dashboard de qualidade."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Apenas descreve as alterações sem gravar.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry = options["dry_run"]
        agora = timezone.now()

        unidades = {
            u.sigla: u
            for u in UnidadeAdministrativa.objects.filter(
                sigla__in=("ZEL", "ILUM", "SLU")
            )
        }
        if len(unidades) < 3:
            self.stderr.write("Unidades ZEL/ILUM/SLU não encontradas.")
            return

        servicos_por_nome = {
            s.nome: s
            for s in ServicoCatalogo.objects.filter(
                nome__in=(
                    "Buracos e Pavimentação",
                    "Iluminação Pública",
                    "Limpeza Urbana",
                )
            )
        }
        for nome, sigla in (
            ("Iluminação Pública", "ILUM"),
            ("Limpeza Urbana", "SLU"),
            ("Buracos e Pavimentação", "ZEL"),
        ):
            srv = servicos_por_nome.get(nome)
            if srv and unidades.get(sigla):
                if not dry and srv.unidade_responsavel_id != unidades[sigla].id:
                    srv.unidade_responsavel = unidades[sigla]
                    srv.save(update_fields=["unidade_responsavel"])

        # (codigo, servico_nome, nota, dentro_sla, qtde_extra_resolvidos simulados via mesmo proto)
        cenarios = [
            ("PROT-2026-002", "Iluminação Pública", 5, True),
            ("PROT-2026-004", "Limpeza Urbana", 2, False),
            ("PROT-2026-006", "Buracos e Pavimentação", 4, True),
            ("PROT-2026-007", "Iluminação Pública", 3, False),
            ("PROT-2026-005", "Buracos e Pavimentação", 1, False),
        ]

        alterados = 0
        for codigo, servico_nome, nota, dentro_sla in cenarios:
            try:
                proto = Protocolo.objects.select_related("servico").get(codigo=codigo)
            except Protocolo.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Protocolo {codigo} não encontrado."))
                continue

            srv = servicos_por_nome.get(servico_nome)
            if not srv:
                self.stdout.write(self.style.WARNING(f"Serviço {servico_nome} não encontrado."))
                continue

            sla_horas = int(srv.sla_horas or 72)
            prazo = proto.data_criacao + timedelta(hours=sla_horas)
            if dentro_sla:
                fechamento = min(prazo - timedelta(hours=2), agora - timedelta(hours=1))
            else:
                fechamento = max(prazo + timedelta(hours=6), agora - timedelta(minutes=30))

            self.stdout.write(
                f"{codigo} → {servico_nome} | nota={nota} | "
                f"SLA {'OK' if dentro_sla else 'VENCIDO'}"
            )

            if dry:
                alterados += 1
                continue

            if proto.servico_id != srv.id:
                Protocolo.objects.filter(pk=proto.pk).update(servico_id=srv.id)

            Protocolo.objects.filter(pk=proto.pk).update(
                status=Protocolo.Status.RESOLVIDO,
                nota_satisfacao=nota,
                comentario_satisfacao=f"Avaliação demo matriz qualidade (nota {nota}).",
                data_atualizacao=fechamento,
            )
            alterados += 1

        msg = f"{alterados} protocolo(s) preparados para a matriz de qualidade."
        if dry:
            self.stdout.write(self.style.WARNING(f"[dry-run] {msg}"))
        else:
            self.stdout.write(self.style.SUCCESS(msg))