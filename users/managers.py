from django.db import models

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
            return self.select_related('user').get(
                verification_code=code, is_verified=False)
        except user_models.Profile.DoesNotExist:  # ignore
            return None
