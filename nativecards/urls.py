"""
Nativecards URL Configuration
"""
from cards.urls import router as cards_router
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from two_factor.urls import urlpatterns as tf_urls
from users.urls import ROUTER as USERS_ROUTER

from .routers import DefaultRouter
from .views import SettingsViewSet

BASE_ROUTER = SimpleRouter()
BASE_ROUTER.register(r'settings', SettingsViewSet, 'settings')

ROUTER = DefaultRouter()
ROUTER.extend(cards_router)
ROUTER.extend(USERS_ROUTER)
ROUTER.extend(BASE_ROUTER)

urlpatterns = [
    path('management/', admin.site.urls),
    re_path(r'^api-token-auth/',
            TokenObtainPairView.as_view(),
            name='token_obtain_pair'),
    re_path(r'^api-token-refresh/',
            TokenRefreshView.as_view(),
            name='token_refresh'),
    re_path(r'^markdownx/', include('markdownx.urls')),
    path(r'', include(tf_urls)),
]

urlpatterns += i18n_patterns(re_path(r'^', include(ROUTER.urls)), )

if settings.DEBUG or settings.TESTS:
    import debug_toolbar

    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
