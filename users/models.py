from annoying.fields import AutoOneToOneField
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel


class Profile(TimeStampedModel):
    """
    User profile class
    """
    user = AutoOneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    is_verified = models.BooleanField(
        default=True, db_index=True, verbose_name=_('is verified'))
    verification_code = models.CharField(
        max_length=100, null=True, blank=True, db_index=True)

    def __str__(self):
        return "{}'s profile".format(self.user.username)
