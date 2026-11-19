"""Paginação no formato definido pelo API_CONTRACT.md."""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ContractPagination(PageNumberPagination):
    """Resposta com chaves `data` e `pagination`."""

    page_query_param = "page"
    page_size_query_param = "per_page"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "data": data,
                "pagination": {
                    "current_page": self.page.number,
                    "per_page": self.get_page_size(self.request),
                    "total_items": self.page.paginator.count,
                    "total_pages": self.page.paginator.num_pages,
                },
            }
        )
