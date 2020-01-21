"""
The cards view module
"""
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_extensions.cache.mixins import CacheResponseMixin

import nativecards.lib.settings as config
from nativecards.lib.dictionary import get_definition
from nativecards.lib.pixabay import get_images
from nativecards.lib.synonyms import get_synonyms
from nativecards.lib.trans import translate
from nativecards.viewsets import UserFilterViewSetMixin

from .filters import CardFilter
from .lesson.generator import LessonGenerator
from .models import Attempt, Card, Deck
from .serializers import (AttemptSerializer, CardSerializer, DeckSerializer,
                          LessonCardSerializer)


class DeckViewSet(UserFilterViewSetMixin, CacheResponseMixin,
                  viewsets.ModelViewSet):
    """
    The decks viewset class
    """
    search_fields = ('=id', 'title', 'description', 'created_by__username',
                     'created_by__email', 'created_by__last_name')

    serializer_class = DeckSerializer
    filterset_fields = ('is_default', 'is_enabled', 'created')

    def get_query_to_filter(self):
        """
        Returns a query to filter
        """
        return Deck.objects.all()


class CardViewSet(UserFilterViewSetMixin, viewsets.ModelViewSet):
    """
    The cards viewset class
    """
    search_fields = ('=id', 'word', 'translation', 'created_by__username',
                     'created_by__email', 'created_by__last_name')

    serializer_class = CardSerializer
    filterset_class = CardFilter
    select_related = ['deck']

    def get_serializer_class(self):
        if self.action == 'lesson':
            return LessonCardSerializer
        return super().get_serializer_class()

    def get_query_to_filter(self):
        """
        Returns a query to filter
        """
        return Card.objects.all()

    @staticmethod
    @action(detail=False, methods=['get'])
    def images(request):
        """
        Returns images for a word
        """
        result = get_images(request.GET.get('word'))
        return Response(result, status=200)

    @staticmethod
    @action(detail=False, methods=['get'])
    def translation(request):
        """
        Returns translations for a word
        """
        result = translate(
            request.GET.get('word'),
            config.get('language', request.user),
        )
        return Response(result, status=200)

    @staticmethod
    @action(detail=False, methods=['get'])
    def synonyms(request):
        """
        Returns synonyms and antonyms for a word
        """
        result = get_synonyms(request.GET.get('word'))
        return Response(result, status=200)

    @staticmethod
    @action(detail=False, methods=['get'])
    def definition(request):
        """
        Returns definitions for a word
        """
        result = get_definition(request.GET.get('word'))
        return Response(result, status=200)

    @action(detail=False, methods=['get'])
    def lesson(self, request):
        """
        Returns words for a lesson
        """
        lesson = LessonGenerator(request)
        return Response(
            self.get_serializer(lesson.get_lesson_cards(), many=True).data)


class AttemptViewSet(UserFilterViewSetMixin, mixins.CreateModelMixin,
                     mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    The attempts viewset class
    """
    search_fields = ('=pk', 'card__word', 'answer', 'created_by__username',
                     'created_by__email', 'created_by__last_name')

    serializer_class = AttemptSerializer
    filterset_fields = ('is_correct', 'is_hint', 'created_by', 'created')

    def get_query_to_filter(self):
        """
        Returns a query to filter
        """
        return Attempt.objects.all()

    @staticmethod
    @action(detail=False, methods=['get'])
    def statistics(request):
        """
        Returns user statistics
        """
        return Response(Attempt.objects.get_statistics(request.user))
