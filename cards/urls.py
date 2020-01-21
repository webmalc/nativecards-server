"""
The cards urls module
"""
from rest_framework.routers import SimpleRouter

from .views import AttemptViewSet, CardViewSet, DeckViewSet

ROUTER = SimpleRouter()
ROUTER.register(r'decks', DeckViewSet, 'decks')
ROUTER.register(r'cards', CardViewSet, 'cards')
ROUTER.register(r'attempts', AttemptViewSet, 'attempts')
