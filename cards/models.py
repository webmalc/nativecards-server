from django.core.validators import (MaxValueValidator, MinLengthValidator,
                                    MinValueValidator)
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel, TitleDescriptionModel
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from ordered_model.models import OrderedModel

from nativecards.models import CommonInfo


class ImageMixin(models.Model):
    """
    The mixin with the images fields.
    """
    image = ProcessedImageField(
        upload_to='uploads',
        processors=[ResizeToFill(150)],
        format='JPG',
        options={'quality': 60},
        null=True,
        blank=True,
        verbose_name=_('image'),
    )
    remote_image = models.URLField(
        null=True, blank=True, verbose_name=_('remote image url'))

    class Meta:
        abstract = True


class Deck(CommonInfo, TimeStampedModel, TitleDescriptionModel, OrderedModel,
           ImageMixin):
    """
    The flashcard's deck class
    """

    is_default = models.BooleanField(
        default=True, db_index=True, verbose_name=_('is default'))

    class Meta(OrderedModel.Meta):
        pass


class Card(CommonInfo, TimeStampedModel, ImageMixin):
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
        verbose_name=_('definition'),
        validators=[MinLengthValidator(2)])
    translation = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('translation'),
        validators=[MinLengthValidator(2)])
    pronunciation = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        validators=[MinLengthValidator(2)],
        verbose_name=_('pronunciation'))
    complete = models.PositiveIntegerField(
        default=0,
        verbose_name=_('complete'),
        validators=[MinValueValidator(1),
                    MaxValueValidator(100)])
    priority = models.PositiveIntegerField(
        default=2, choices=PRIORITY, verbose_name=_('priority'), db_index=True)
    last_showed_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_('last showed at'))
    deck = models.ForeignKey(
        Deck,
        on_delete=models.CASCADE,
        db_index=True,
        related_name='cards',
        verbose_name=_('deck'))
