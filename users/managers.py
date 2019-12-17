"""
The users managers module
"""
from time import time_ns

from django.contrib.auth.models import User
from django.db import models

from nativecards.models import Settings
from users import models as user_models


class ProfileManager(models.Manager):
    """"
    The profile manager
    """
    def get_by_code(self, code: str):
        """
        Get a user profile by a code
        """
        try:
            return self.select_related('user').get(verification_code=code,
                                                   is_verified=False)
        except user_models.Profile.DoesNotExist:  # ignore
            return None

    @staticmethod
    def create_user(email: str, password: str, language: str) -> User:
        """
        Create a user account by email
        """
        user = User()
        user.username = email
        user.email = email
        user.set_password(password)
        user.full_clean()
        user.save()
        code = User.objects.make_random_password(60) + str(time_ns())
        user.profile.verification_code = code
        user.profile.is_verified = False
        user.profile.save()

        settings = Settings.objects.get_by_user(user)
        settings.language = language
        settings.full_clean()
        settings.save()

        return user
