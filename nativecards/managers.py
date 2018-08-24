from abc import ABCMeta, abstractproperty
from functools import reduce

from django.db import models
from django.db.models import Q

import nativecards


class LookupMixin(models.Manager, metaclass=ABCMeta):
    """
    The LookupMixin
    """

    @abstractproperty
    def lookup_search_fields(self):
        return ('pk', )

    def lookup(self, q, request):
        """
        Base lookup query
        """

        return self.filter(
            reduce(lambda x, f: x | Q(**{'%s__icontains' % f: q}),
                   self.lookup_search_fields, Q()))[:100]


class DictManager(models.Manager):
    """
    The default manager for DictMixin
    """

    def filter_is_enabled(self):
        return self.filter(is_enabled=True)


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
