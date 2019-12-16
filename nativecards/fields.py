"""
The base fields module
"""
from django.conf import settings
from django.db.models.fields import CharField
from django.utils.translation import ugettext_lazy as _


class LanguageField(CharField):
    """
    The language field for Django models.
    """

    description = _("Language code")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 2)
        kwargs.setdefault('choices', settings.LANGUAGES)
        super().__init__(*args, **kwargs)
