"""
Nativecards URL Configuration
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls.i18n import i18n_patterns
from ajax_select import urls as ajax_select_urls
from django.conf import settings
from two_factor.urls import urlpatterns as tf_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'', include(tf_urls)),
]

urlpatterns += i18n_patterns(
    re_path(r'^ajax_select/', include(ajax_select_urls)), )

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
