from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    page_size = 5
