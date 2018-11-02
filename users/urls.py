from rest_framework.routers import SimpleRouter

from .views import UsersViewSet

router = SimpleRouter()
router.register(r'users', UsersViewSet, 'users')
