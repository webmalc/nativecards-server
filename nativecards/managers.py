"""
The base managers module
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import nativecards
from django.db import models

if TYPE_CHECKING:
    from users.models import User
    from .models import Settings


class SettingsManager(models.Manager):
    """
    The settings objects manager
    """
    def get_by_user(self, user: User) -> Settings:
        """
        Get user's settings
        """
        try:
            return self.filter(created_by=user).get()
        except nativecards.models.Settings.DoesNotExist:
            settings = self.create(created_by=user)
            return settings

    def update_by_user(self, user: User, **kwargs) -> Settings:
        """
        Update user's settings
        """
        settings = self.get_by_user(user)
        for key, attr in kwargs.items():
            setattr(settings, key, attr)
        settings.full_clean()
        settings.save()

        return settings
