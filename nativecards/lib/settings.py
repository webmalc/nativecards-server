"""
The settings lib
"""
from typing import Generator

from django.conf import settings
from django.utils.module_loading import import_string

from nativecards.models import Settings

SETTINGS = {}  # type: ignore
RELOAD = False  # type: ignore


def get_instances(key: str) -> Generator:
    """
    Gets class instances from the settings
    """
    modules = getattr(settings, 'NC_' + key.upper(), [])
    for name in modules:
        yield import_string(name)()


def get(key: str, user=None):
    """
    Get settings
    """
    default = getattr(settings, 'NC_' + key.upper(), None)
    if user:
        if user.id not in SETTINGS or RELOAD:
            user_settings = Settings.objects.get_by_user(user)
            SETTINGS[user.id] = user_settings
        return getattr(SETTINGS[user.id], key, default)
    return default


def clear_mermory_cache(user):
    """
    Clear user settings in-memory cache
    """
    return SETTINGS.pop(user.id, None)
