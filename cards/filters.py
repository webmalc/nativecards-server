"""
The cards filters module
"""
from django_filters import rest_framework as filters

from .models import Card


class CardFilter(filters.FilterSet):
    """
    The filter class for the cards viewset class
    """
    complete__gte = filters.NumberFilter(field_name='complete',
                                         label='complete greater',
                                         lookup_expr='gte')

    complete__lte = filters.NumberFilter(field_name='complete',
                                         label='complete less',
                                         lookup_expr='lte')

    word_starts = filters.CharFilter(field_name='word',
                                     label='word starts with',
                                     lookup_expr='istartswith')

    class Meta:
        """
        Meta class
        """
        model = Card
        fields = ('deck', 'priority', 'category', 'complete', 'complete__gte',
                  'complete__lte', 'created_by', 'created', 'last_showed_at',
                  'is_enabled')
