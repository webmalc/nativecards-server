from nativecards.viewsets import UserModelViewSet

from .models import Deck
from .serializers import DeckSerializer


class DeckViewSet(UserModelViewSet):
    search_fields = ('=id', 'ip', 'client__name', 'client__email',
                     'client__login', 'user_agent')

    serializer_class = DeckSerializer
    filter_fields = ('is_default', 'is_enabled', 'created')

    def get_queryset(self):
        return self.filter_by_user(Deck.objects.all())
