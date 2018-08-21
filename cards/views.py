from rest_framework.decorators import list_route
from rest_framework.response import Response

from nativecards.lib.pixabay import get_images
from nativecards.viewsets import UserModelViewSet

from .models import Card, Deck
from .serializers import CardSerializer, DeckSerializer


class DeckViewSet(UserModelViewSet):
    search_fields = ('=id', 'ip', 'client__name', 'client__email',
                     'client__login', 'user_agent')

    serializer_class = DeckSerializer
    filter_fields = ('is_default', 'is_enabled', 'created')

    def get_queryset(self):
        return self.filter_by_user(Deck.objects.all())


class CardViewSet(UserModelViewSet):
    search_fields = ('=pk', 'word', 'definition', 'translation', 'examples',
                     'created_by__username', 'created_by__email',
                     'created_by__last_name')

    serializer_class = CardSerializer
    filter_fields = ('deck', 'priority', 'complete', 'created_by', 'created',
                     'last_showed_at', 'is_enabled')

    def get_queryset(self):
        return self.filter_by_user(Card.objects.all()).select_related('deck')

    @list_route(methods=['get'])
    def images(self, request, login=None):
        return Response(get_images(request.GET.get('word')))
