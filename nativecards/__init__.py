"""
The nativecards init module
"""
# pylint: disable=invalid-name
from __future__ import absolute_import

from .celery_app import app as celery_app

default_app_config = 'nativecards.apps.NativecardsConfig'

__all__ = ('celery_app', 'default_app_config')
