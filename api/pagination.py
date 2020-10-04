from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    page_size = 25

    def paginate_queryset(self, queryset, request, view=None):
        if 'no_page' in request.query_params:
            return None
        return pagination.PageNumberPagination.paginate_queryset(self, queryset, request)
