from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from .managers import SettingsManager


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


class CachedModel(models.Model):
    class Meta:
        abstract = True


class Settings(CachedModel, CommonInfo, TimeStampedModel):  # type: ignore
    """
    The class with user settings
    """

    objects = SettingsManager()

    attempts_to_remember = models.PositiveIntegerField(
        default=settings.NC_ATTEMPTS_TO_REMEMBER,
        verbose_name=_('attempts to remember'),
        help_text=_('number of correct answers to remember the card'),
        validators=[MinValueValidator(3),
                    MaxValueValidator(50)])
    cards_per_lesson = models.PositiveIntegerField(
        default=settings.NC_CARDS_PER_LESSON,
        verbose_name=_('cards per lesson'),
        help_text=_('number of cards to study per the lesson'),
        validators=[MinValueValidator(5),
                    MaxValueValidator(50)])
    cards_to_repeat = models.PositiveIntegerField(
        default=settings.NC_CARDS_TO_REPEAT,
        verbose_name=_('cards to repeat'),
        help_text=_('number of cards to repeat per the lesson'),
        validators=[MinValueValidator(0),
                    MaxValueValidator(50)])
    lesson_latest_days = models.PositiveIntegerField(
        default=settings.NC_LESSON_LATEST_DAYS,
        verbose_name=_('lesson latest days'),
        help_text=_('number of days for getting the latest added cards'),
        validators=[MinValueValidator(5),
                    MaxValueValidator(50)])
    lessons_per_day = models.PositiveIntegerField(
        default=settings.NC_LESSONS_PER_DAY,
        verbose_name=_('lessons per day'),
        help_text=_('number of lessons to complete per day'),
        validators=[MinValueValidator(0),
                    MaxValueValidator(50)])
    play_audio_on_open = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_('play audio when the card is opening'),
        verbose_name=_('play audio on open'))

    @property
    def attempts_per_day(self) -> int:
        return self.lessons_per_day * (
            self.cards_per_lesson * settings.NC_CARDS_REPEAT_IN_LESSON +
            self.cards_to_repeat)

    def __str__(self):
        return "{}'s settings".format(self.created_by)

    class Meta:
        ordering = ['-created']
        verbose_name_plural = _('settings')
