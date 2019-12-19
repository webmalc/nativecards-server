"""
The words managers module
"""
from __future__ import annotations

from typing import Optional

from django.db import models

import words.models
from nativecards.lib.dicts.base import DictionaryEntry


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
    ) -> Optional[words.models.Word]:
        """
        Create or update the word
        """
        params = locals()
        del params['word']
        del params['self']
        if not any(params.values()):
            return None
        word, _ = self.get_or_create(word=word)
        if translation and language:
            word.translations[language] = translation
        if synonyms:
            word.synonyms = synonyms
        if antonyms:
            word.antonyms = antonyms
        if definition:
            for key, value in definition.__dict__.items():
                if value:
                    setattr(word, key, value)
        word.save()

        return word
