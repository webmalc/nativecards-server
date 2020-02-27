"""
The celery module
"""
from __future__ import absolute_import

import os

from django.conf import settings

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nativecards.settings')
app = Celery('nativecards')  # pylint: disable=invalid-name

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
