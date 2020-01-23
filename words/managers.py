"""
The words managers module
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from django.db import models

from nativecards.lib.dicts.base import DictionaryEntry

if TYPE_CHECKING:
    from .models import Word


class WordManager(models.Manager):
    """"
    The word objects manager
    """
    def create_or_update(
            self,
            word: str,
            definition: Optional[DictionaryEntry] = None,
            translation: Optional[str] = None,
            language: Optional[str] = None,
            synonyms: Optional[str] = None,
            antonyms: Optional[str] = None,
    ) -> Optional[Word]:
        """
        Create or update the word
        """
        params = locals()
        del params['word']
        del params['self']
        if not any(params.values()):
            return None
        word_object, _ = self.get_or_create(word=word)
        if translation and language:
            word_object.translations[language] = translation
        if synonyms:
            word_object.synonyms = synonyms
        if antonyms:
            word_object.antonyms = antonyms
        if definition:
            for key, value in definition.__dict__.items():
                if value:
                    setattr(word_object, key, value)
        word_object.save()

        return word_object

    def get_with_translation(self, word: str, language: str) -> Optional[Word]:
        """
        Get a words object based on the translation
        """
        return self.filter(
            word=word,
            translations__has_key=language,
        ).first()
