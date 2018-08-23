from rest_framework.routers import SimpleRouter

from .views import AttemptViewSet, CardViewSet, DeckViewSet

router = SimpleRouter()
router.register(r'decks', DeckViewSet, 'decks')
router.register(r'cards', CardViewSet, 'cards')
router.register(r'attempts', AttemptViewSet, 'attempts')
