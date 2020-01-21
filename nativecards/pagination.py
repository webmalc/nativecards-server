"""
The pagination module
"""
from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """
    The pagination class
    """
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 1000
