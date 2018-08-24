from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel


class CommonInfo(models.Model):
    """ CommonInfo abstract model """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        db_index=True,
        on_delete=models.SET_NULL,
        verbose_name=_('created by'),
        related_name="%(app_label)s_%(class)s_created_by")
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        db_index=True,
        on_delete=models.SET_NULL,
        editable=False,
        verbose_name=_('modified by'),
        related_name="%(app_label)s_%(class)s_modified_by")
    is_enabled = models.BooleanField(
        default=True, db_index=True, verbose_name=_('is enabled'))

    def __str__(self):
        default = '{} #{}'.format(type(self).__name__, str(self.id))
        return getattr(self, 'name', getattr(self, 'title', default))

    class Meta:
        abstract = True


# class Settings(CommonInfo, TimeStampedModel):
#     """
#     The class with user settings
#     """

#     # NC_ATTEMPTS_TO_REMEMBER = 10
#     # NC_CARDS_PER_LESSON = 10
#     # NC_CARDS_TO_REPEAT = 5
#     # NC_LESSON_LATEST_DAYS = 21
#     attempts_to_remeber = models.PositiveIntegerField(
#         default=settings.NC_ATTEMPTS_TO_REMEMBER,
#         verbose_name=_('complete'),
#         validators=[MinValueValidator(0),
#                     MaxValueValidator(100)])


class CachedModel(models.Model):
    class Meta:
        abstract = True
