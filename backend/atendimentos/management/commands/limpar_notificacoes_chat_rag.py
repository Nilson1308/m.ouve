"""Remove notificações espúrias geradas por turnos do chat RAG (Sprint 4.5)."""

from django.core.management.base import BaseCommand
from django.db.models import Q

from atendimentos.models import NotificacaoCidadao

TITULOS_CHAT_RAG = (
    "Nova mensagem na conversa",
    "Nova mensagem no seu protocolo",
)


def queryset_notificacoes_chat_rag():
    """Notificações típicas do antigo `notificar_resposta_ia_chat` — não são marcos de protocolo."""
    assinatura_ia = Q(mensagem__icontains="Assistente M.Ouve")
    titulo_chat = Q(titulo__in=TITULOS_CHAT_RAG) | Q(titulo__icontains="Assistente")
    sem_protocolo = Q(protocolo__isnull=True)
    return NotificacaoCidadao.objects.filter(titulo_chat & (assinatura_ia | sem_protocolo))


class Command(BaseCommand):
    help = (
        "Remove notificações in-app criadas por respostas do chat RAG. "
        "Use --dry-run para apenas contar."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Apenas exibe quantas seriam removidas, sem apagar.",
        )

    def handle(self, *args, **options):
        qs = queryset_notificacoes_chat_rag()
        total = qs.count()
        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING(f"[dry-run] {total} notificação(ões) seriam removidas.")
            )
            return
        deleted, _ = qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Removidas {deleted} notificação(ões) de chat RAG."))