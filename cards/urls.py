from rest_framework.routers import SimpleRouter

from .views import CardViewSet, DeckViewSet

router = SimpleRouter()
router.register(r'decks', DeckViewSet, 'decks')
router.register(r'cards', CardViewSet, 'cards')
