from django_filters import rest_framework as filters
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from nativecards.lib.dictionary import definition, synonyms
from nativecards.lib.pixabay import get_images
from nativecards.lib.trans import translate
from nativecards.viewsets import UserViewSetMixin

from .lesson import LessonGenerator
from .models import Attempt, Card, Deck
from .serializers import AttemptSerializer, CardSerializer, DeckSerializer


class DeckViewSet(CacheResponseMixin, viewsets.ModelViewSet, UserViewSetMixin):
    search_fields = ('=id', 'title', 'description', 'created_by__username',
                     'created_by__email', 'created_by__last_name')

    serializer_class = DeckSerializer
    filterset_fields = ('is_default', 'is_enabled', 'created')

    def get_queryset(self):
        return self.filter_by_user(Deck.objects.all())


class CardFilter(filters.FilterSet):
    complete__gte = filters.NumberFilter(
        field_name='complete', label='complete greater', lookup_expr='gte')

    complete__lte = filters.NumberFilter(
        field_name='complete', label='complete less', lookup_expr='lte')

    class Meta:
        model = Card
        fields = ('deck', 'priority', 'category', 'complete', 'complete__gte',
                  'complete__lte', 'created_by', 'created', 'last_showed_at',
                  'is_enabled')


class CardViewSet(viewsets.ModelViewSet, UserViewSetMixin):
    search_fields = ('=id', 'word', 'definition', 'translation', 'examples',
                     'created_by__username', 'created_by__email',
                     'created_by__last_name')

    serializer_class = CardSerializer
    filterset_class = CardFilter

    def get_queryset(self):
        return self.filter_by_user(Card.objects.all()).select_related('deck')

    @action(detail=False, methods=['get'])
    def images(self, request):
        return Response(get_images(request.GET.get('word')))

    @action(detail=False, methods=['get'])
    def translation(self, request):
        return Response(translate(request.GET.get('word')))

    @action(detail=False, methods=['get'])
    def synonyms(self, request):
        return Response(synonyms(request.GET.get('word')))

    @action(detail=False, methods=['get'])
    def definition(self, request):
        return Response(definition(request.GET.get('word')))

    @action(detail=False, methods=['get'])
    def lesson(self, request):
        lesson = LessonGenerator(request, self.get_serializer)
        return Response(lesson.get_lesson_cards())


class AttemptViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet, UserViewSetMixin):

    search_fields = ('=pk', 'card__word', 'answer', 'created_by__username',
                     'created_by__email', 'created_by__last_name')

    serializer_class = AttemptSerializer
    filterset_fields = ('is_correct', 'is_hint', 'created_by', 'created')

    def get_queryset(self):
        return self.filter_by_user(Attempt.objects.all())

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        return Response(Attempt.objects.get_statistics(request.user))
