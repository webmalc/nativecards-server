from rest_framework.routers import SimpleRouter

from .views import DeckViewSet

router = SimpleRouter()
router.register(r'decks', DeckViewSet, 'decks')
