"""
Nativecards URL Configuration
"""
from ajax_select import urls as ajax_select_urls
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from two_factor.urls import urlpatterns as tf_urls

from cards.urls import router as cards_router
from users.urls import router as users_router

from .routers import DefaultRouter
from .views import SettingsViewSet

base_router = SimpleRouter()
base_router.register(r'settings', SettingsViewSet, 'settings')

router = DefaultRouter()
router.extend(cards_router)
router.extend(users_router)
router.extend(base_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^api-token-auth/',
            TokenObtainPairView.as_view(),
            name='token_obtain_pair'),
    re_path(r'^api-token-refresh/',
            TokenRefreshView.as_view(),
            name='token_refresh'),
    re_path(r'^markdownx/', include('markdownx.urls')),
    path(r'', include(tf_urls)),
]

urlpatterns += i18n_patterns(
    re_path(r'^ajax_select/', include(ajax_select_urls)),
    re_path(r'^', include(router.urls)),
)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
