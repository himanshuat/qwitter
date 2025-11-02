from rest_framework.pagination import PageNumberPagination


class QwitterPagination(PageNumberPagination):
    """
    Default pagination class for the Qwitter API.
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50
