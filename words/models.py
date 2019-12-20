"""
The words models module
"""
from django.contrib.postgres.fields import HStoreField
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from markdownx.models import MarkdownxField
from nativecards.lib.dictionary import guess_category
from nativecards.models import CommonInfo

from .managers import WordManager


class BaseWord(CommonInfo, TimeStampedModel):
    """
    Base word class
    """
    CATEGORIES = (
        ('word', _('word')),
        ('phrase', _('phrase')),
        ('phrasal_verb', _('phrasal verb')),
    )

    word = models.CharField(max_length=255,
                            db_index=True,
                            validators=[MinLengthValidator(2)],
                            verbose_name=_('word'))
    category = models.CharField(max_length=30,
                                null=True,
                                blank=True,
                                db_index=True,
                                choices=CATEGORIES,
                                verbose_name=_('category'))
    definition = MarkdownxField(db_index=True,
                                null=True,
                                blank=True,
                                verbose_name=_('definition'),
                                validators=[MinLengthValidator(2)])
    examples = MarkdownxField(null=True,
                              blank=True,
                              db_index=True,
                              verbose_name=_('examples'),
                              validators=[MinLengthValidator(2)])
    synonyms = MarkdownxField(null=True,
                              blank=True,
                              db_index=True,
                              verbose_name=_('synonyms'),
                              validators=[MinLengthValidator(2)])
    antonyms = MarkdownxField(null=True,
                              blank=True,
                              db_index=True,
                              verbose_name=_('antonyms'),
                              validators=[MinLengthValidator(2)])
    transcription = models.CharField(max_length=255,
                                     null=True,
                                     blank=True,
                                     db_index=True,
                                     verbose_name=_('transcription'),
                                     validators=[MinLengthValidator(2)])
    pronunciation = models.URLField(null=True,
                                    blank=True,
                                    verbose_name=_('pronunciation'))

    def _guess_and_set_category(self) -> None:
        """
        Try to guess and set the word category
        """
        if not self.category:
            self.category = guess_category(self.word)

    class Meta:
        abstract = True


class Word(BaseWord):
    """
    The word class
    """

    objects = WordManager()

    translations = HStoreField(
        null=True,
        blank=True,
        db_index=True,
        default=dict,
        verbose_name=_('translations'),
    )

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        self._guess_and_set_category()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('word', )
        unique_together = (("word", ), )
