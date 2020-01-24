"""
The settings lib
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator, Optional

from django.conf import settings
from django.utils.module_loading import import_string

from nativecards.models import Settings

SETTINGS = {}  # type: ignore
RELOAD = False  # type: ignore


class Chain(ABC):
    """
    The base chain class
    """
    successor: Optional[Chain] = None

    @abstractmethod
    def get_result(self, **kwargs):
        """
        Gets results
        """

    def check(self, **kwargs) -> bool:
        """
        Checks if the class is applicable
        """
        # pylint: disable=no-self-use, unused-argument
        return True

    def handle(self, **kwargs):
        """
        Goes down the chain of responsibility
        """
        if self.check(**kwargs):
            result = self.get_result(**kwargs)
            if result:
                return result
        if self.successor:
            return self.successor.handle(**kwargs)
        return None


def get_chain(key: str) -> Chain:
    """
    Gets a chain of responsibility from the settings
    """
    modules = get_instances(key)
    first: Chain = next(modules)
    prev: Chain = first
    for element in modules:
        if prev and prev != element:
            prev.successor = element
        prev = element

    return first


def get_instances(key: str) -> Iterator[Chain]:
    """
    Gets class instances from the settings
    """
    modules = getattr(settings, 'NC_' + key.upper(), [])
    if not modules:
        raise ValueError('Invalid key has been provided')
    for name in modules:
        yield import_string(name)()


def get(key: str, user=None):
    """
    Get settings
    """
    default = getattr(settings, 'NC_' + key.upper(), None)
    if not user:
        return default

    if user.id not in SETTINGS or RELOAD:
        user_settings = Settings.objects.get_by_user(user)
        SETTINGS[user.id] = user_settings
    return getattr(SETTINGS[user.id], key, default)


def clear_mermory_cache(user):
    """
    Clear user settings in-memory cache
    """
    return SETTINGS.pop(user.id, None)
