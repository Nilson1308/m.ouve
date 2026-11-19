"""Kanban unificado da Mesa de Trabalho."""

from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from atendimentos.backoffice_views import IsBackofficeStaff
from atendimentos.kanban_services import montar_kanban_unificado


class KanbanPagination(PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "per_page"
    page_size = 50
    max_page_size = 200


class BackofficeKanbanView(APIView):
    """
    GET — itens mesclados: protocolos sem Super OS + incidentes Super OS.
    Ordenação: SLA/urgência (vencido → tempo restante → urgência).
    """

    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request):
        itens = montar_kanban_unificado(request.query_params, user=request.user)
        paginator = KanbanPagination()
        page = paginator.paginate_queryset(itens, request, view=self)
        if page is None:
            return Response({"data": itens, "count": len(itens)})
        return Response(
            {
                "data": page,
                "count": len(itens),
                "pagination": {
                    "current_page": paginator.page.number,
                    "per_page": paginator.get_page_size(request),
                    "total_items": paginator.page.paginator.count,
                    "total_pages": paginator.page.paginator.num_pages,
                },
            }
        )