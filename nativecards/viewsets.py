"""
The nativecards viewsets module
"""
from abc import ABC, abstractmethod
from typing import List


class UserFilterViewSetMixin(ABC):
    """
    The mixin with created_by field filter
    """
    select_related: List[str] = []

    @abstractmethod
    def get_query_to_filter(self):
        """
        Returns a query to filter
        """

    def filter_by_user(self, query):
        """
        Filter the query by the request user
        """
        select_related = ['created_by', 'modified_by'] + self.select_related
        return query.filter(
            created_by=self.request.user).select_related(*set(select_related))

    def get_queryset(self):
        """
        Get an query
        """
        return self.filter_by_user(self.get_query_to_filter())
