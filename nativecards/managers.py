"""
The base managers module
"""
from django.db import models

import nativecards


class SettingsManager(models.Manager):
    """"
    The settings objects manager
    """

    def get_by_user(self, user):
        """
        Get user's settings
        """
        try:
            return self.filter(created_by=user).get()
        except nativecards.models.Settings.DoesNotExist:
            settings = self.create(created_by=user)
            return settings
