"""
The nativecards init module
"""
# pylint: disable=invalid-name, unused-import
from __future__ import absolute_import

from .celery import app as celery_app

default_app_config = 'nativecards.apps.NativecardsConfig'
