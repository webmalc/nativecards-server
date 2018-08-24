from random import shuffle

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from nativecards.lib.dictionary import definition
from nativecards.lib.pixabay import get_images
from nativecards.lib.trans import translate
from nativecards.viewsets import UserViewSetMixin

from .models import Attempt, Card, Deck
from .serializers import AttemptSerializer, CardSerializer, DeckSerializer


class DeckViewSet(CacheResponseMixin, viewsets.ModelViewSet, UserViewSetMixin):
    search_fields = ('=id', 'title', 'description', 'created_by__username',
                     'created_by__email', 'created_by__last_name')

    serializer_class = DeckSerializer
    filter_fields = ('is_default', 'is_enabled', 'created')

    def get_queryset(self):
        return self.filter_by_user(Deck.objects.all())


class CardViewSet(viewsets.ModelViewSet, UserViewSetMixin):
    search_fields = ('=pk', 'word', 'definition', 'translation', 'examples',
                     'created_by__username', 'created_by__email',
                     'created_by__last_name')

    serializer_class = CardSerializer
    filter_fields = ('deck', 'priority', 'complete', 'created_by', 'created',
                     'last_showed_at', 'is_enabled')

    def get_queryset(self):
        return self.filter_by_user(Card.objects.all()).select_related('deck')

    @action(detail=False, methods=['get'])
    def images(self, request):
        return Response(get_images(request.GET.get('word')))

    @action(detail=False, methods=['get'])
    def translation(self, request):
        return Response(translate(request.GET.get('word')))

    @action(detail=False, methods=['get'])
    def definition(self, request):
        return Response(definition(request.GET.get('word')))

    @action(detail=False, methods=['get'])
    def lesson(self, request):
        is_latest = bool(request.GET.get('is_latest', 0))
        deck = request.GET.get('deck')
        new_cards = Card.objects.get_lesson_new_cards(
            is_latest,
            request.user,
            deck,
        )
        old_cards = Card.objects.get_lesson_learned_cards(request.user)

        new_cards_data = self.get_serializer(new_cards, many=True).data
        old_cards_data = self.get_serializer(old_cards, many=True).data
        result = new_cards_data * 3 + old_cards_data
        shuffle(result)

        return Response(result)


class AttemptViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet, UserViewSetMixin):

    search_fields = ('=pk', 'card__word', 'answer', 'created_by__username',
                     'created_by__email', 'created_by__last_name')

    serializer_class = AttemptSerializer
    filter_fields = ('is_correct', 'is_hint', 'created_by', 'created')

    def get_queryset(self):
        return self.filter_by_user(Attempt.objects.all())

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        return Response(Attempt.objects.get_statistics(request.user))
