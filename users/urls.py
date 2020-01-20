"""
The users urls module
"""
from rest_framework.routers import SimpleRouter

from .views import UsersViewSet

ROUTER = SimpleRouter()
ROUTER.register(r'users', UsersViewSet, 'users')
