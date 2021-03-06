"""
The cards models module
"""
import shutil
from tempfile import NamedTemporaryFile
from time import time_ns

import requests
from django.conf import settings
from django.core.validators import (MaxValueValidator, MinLengthValidator,
                                    MinValueValidator)
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel, TitleDescriptionModel
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from markdownx.models import MarkdownxField
from ordered_model.models import OrderedModel

from nativecards.models import CachedModel, CommonInfo
from words.models import BaseWord

from .lesson.score import calc_score
from .managers import AttemptManager, CardManager, DeckManager


class ImageMixin(models.Model):
    """
    The mixin with the images fields.
    """
    image = ProcessedImageField(
        upload_to='uploads',
        processors=[ResizeToFit(settings.NC_IMAGE_WIDTH)],
        format='PNG',
        options={'quality': 80},
        null=True,
        blank=True,
        verbose_name=_('image'),
    )
    remote_image = models.URLField(null=True,
                                   blank=True,
                                   verbose_name=_('remote image url'))

    def get_remote_image(self) -> None:
        """
        Saves the image from the remote URL
        """
        if self.remote_image and not self.image:
            response = requests.get(self.remote_image, stream=True)
            img_temp = NamedTemporaryFile(delete=True)
            shutil.copyfileobj(response.raw, img_temp)
            self.image.save('deck_{}_{}.png'.format(time_ns(), self.pk),
                            img_temp)
            self.save()

    class Meta:
        abstract = True


class Deck(  # type: ignore
        CachedModel,
        CommonInfo,
        TimeStampedModel,
        TitleDescriptionModel,
        OrderedModel,
        ImageMixin,
):
    """
    The flashcard's deck class
    """

    objects = DeckManager()

    is_default = models.BooleanField(default=False,
                                     db_index=True,
                                     verbose_name=_('is default'))

    def _reset_decks_default_value(self):
        """
        Save the deck as default and reset the remaining decks
        """
        if self.is_default:
            Deck.objects.filter(is_default=True,
                                created_by=self.created_by).exclude(
                                    pk=self.pk).update(is_default=False)

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        super().save(*args, **kwargs)

        self.get_remote_image()
        self._reset_decks_default_value()

    class Meta(OrderedModel.Meta):
        pass


class Card(BaseWord, ImageMixin):  # type: ignore
    """
    The flashcard class
    """
    PRIORITY = (
        (0, _('very low')),
        (1, _('low')),
        (2, _('normal')),
        (3, _('high')),
        (4, _('very high')),
    )

    objects = CardManager()

    translation = models.CharField(max_length=255,
                                   null=True,
                                   blank=True,
                                   db_index=True,
                                   verbose_name=_('translation'),
                                   validators=[MinLengthValidator(2)])
    note = MarkdownxField(null=True,
                          blank=True,
                          db_index=True,
                          verbose_name=_('note'),
                          validators=[MinLengthValidator(2)])
    complete = models.PositiveIntegerField(
        default=0,
        verbose_name=_('complete'),
        validators=[MinValueValidator(0),
                    MaxValueValidator(100)])
    priority = models.PositiveIntegerField(default=2,
                                           choices=PRIORITY,
                                           verbose_name=_('priority'),
                                           db_index=True)
    last_showed_at = models.DateTimeField(null=True,
                                          blank=True,
                                          verbose_name=_('last showed at'))
    deck = models.ForeignKey(Deck,
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE,
                             db_index=True,
                             related_name='cards',
                             verbose_name=_('deck'))

    def _limit_complete(self) -> None:
        """
        Keep the limit field between 0 and 100
        """
        self.complete = max(0, self.complete)
        self.complete = min(100, self.complete)

    def _set_default_deck(self) -> None:
        """
        Set the default deck if it does not exist
        """
        if not self.deck and self.created_by:
            self.deck = Deck.objects.get_default(self.created_by)
            self.save()

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        self._limit_complete()
        self._guess_and_set_category()

        super().save(*args, **kwargs)

        self.get_remote_image()
        self._set_default_deck()

    def __str__(self):
        return self.word

    class Meta:
        ordering = ('word', )
        unique_together = (("word", "deck"), )


class Attempt(CommonInfo, TimeStampedModel):  # type: ignore
    """
    The card's attempt
    """
    FORMS = (
        ('listen', _('listen')),
        ('write', _('write')),
        ('speak', _('speak')),
    )

    objects = AttemptManager()

    card = models.ForeignKey(Card,
                             on_delete=models.CASCADE,
                             db_index=True,
                             related_name='attempts',
                             verbose_name=_('card'))
    is_correct = models.BooleanField(db_index=True,
                                     verbose_name=_('is correct'))
    is_hint = models.BooleanField(default=False,
                                  db_index=True,
                                  verbose_name=_('is hint'))

    hints_count = models.PositiveIntegerField(default=0,
                                              db_index=True,
                                              verbose_name=_('hints count'))
    answer = models.CharField(max_length=255,
                              blank=True,
                              null=True,
                              db_index=True,
                              validators=[MinLengthValidator(2)],
                              verbose_name=_('answer'))
    score = models.PositiveIntegerField(
        default=0,
        verbose_name=_('score'),
        validators=[MinValueValidator(0),
                    MaxValueValidator(100)])
    form = models.CharField(max_length=30,
                            db_index=True,
                            choices=FORMS,
                            verbose_name=_('form'))

    def _set_score(self) -> None:
        """
        Calculate and set the score
        """
        if not self.pk:
            score = calc_score(self)
            self.score = abs(score)
            self.card.complete = max(0, self.card.complete + score)
            self.card.save()

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        self._set_score()

        super().save(*args, **kwargs)

    def __str__(self):
        return '{} at {}'.format(str(self.card),
                                 self.created.strftime('%d.%m.%Y %H:%M'))

    class Meta:
        ordering = ('-created', )
