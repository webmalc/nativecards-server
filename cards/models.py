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
from ordered_model.models import OrderedModel

from nativecards.models import CommonInfo

from .managers import DeckManager


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
    remote_image = models.URLField(
        null=True, blank=True, verbose_name=_('remote image url'))

    def get_remote_image(self):
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

    is_default = models.BooleanField(
        default=False, db_index=True, verbose_name=_('is default'))

    def save(self, *args, **kwargs):
        # Invoke the parent save method
        super().save(*args, **kwargs)

        # Get an image from remote url
        self.get_remote_image()

        # Update the is default field
        if self.is_default:
            Deck.objects.filter(
                is_default=True, created_by=self.created_by).exclude(
                    pk=self.pk).update(is_default=False)

    class Meta(OrderedModel.Meta):
        pass


class Card(CommonInfo, TimeStampedModel, ImageMixin):  # type: ignore
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
    word = models.CharField(
        max_length=255,
        db_index=True,
        validators=[MinLengthValidator(2)],
        verbose_name=_('word'))
    definition = models.TextField(
        db_index=True,
        verbose_name=_('definition'),
        validators=[MinLengthValidator(2)])
    examples = models.TextField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('examples'),
        validators=[MinLengthValidator(2)])
    translation = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('translation'),
        validators=[MinLengthValidator(2)])
    pronunciation = models.URLField(
        null=True, blank=True, verbose_name=_('pronunciation'))
    complete = models.PositiveIntegerField(
        default=0,
        verbose_name=_('complete'),
        validators=[MinValueValidator(0),
                    MaxValueValidator(100)])
    priority = models.PositiveIntegerField(
        default=2, choices=PRIORITY, verbose_name=_('priority'), db_index=True)
    last_showed_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_('last showed at'))
    deck = models.ForeignKey(
        Deck,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        db_index=True,
        related_name='cards',
        verbose_name=_('deck'))

    def save(self, *args, **kwargs):
        # Invoke the parent save method
        super().save(*args, **kwargs)

        # Get an image from remote url
        self.get_remote_image()

        # Set a default deck
        if not self.deck and self.created_by:
            self.deck = Deck.objects.get_default(self.created_by)
            self.save()

    class Meta:
        ordering = ('word', )
