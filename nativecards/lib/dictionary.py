"""
The dictionary module
"""
from __future__ import annotations

from typing import Optional

from django.db.models.query import QuerySet

from .audio import get_audio
from .cache import cache_result
from .dicts.models import BaseManager, DictionaryEntry, manager_runner


class DictionaryManager(BaseManager):
    """
    The dictionary manager
    """
    settings_key: str = 'DICTIONARIES'
    word_fields = ['definition', 'examples', 'pronunciation', 'transcription']

    @property
    def word_query(self) -> QuerySet:
        return self.word_model.objects.get_with_definition

    @staticmethod
    def is_result_valid(result: Optional[DictionaryEntry]) -> bool:
        """
        Checks result
        """
        return bool(result and result.definition)

    def process_result(self, result: DictionaryEntry) -> DictionaryEntry:
        """
        Processes result
        """
        if not result.pronunciation:
            result.pronunciation = get_audio(self.word)
        return result


@cache_result('definition')
def get_definition(word) -> Optional[dict]:
    """
    Get the word's definition
    """
    return manager_runner(word, DictionaryManager)


def guess_category(word: str) -> str:
    """
    Try to guess the word category
    """
    pieces = word.split(' ')
    category = 'word'
    if 1 < len(pieces) <= 3:
        category = 'phrasal_verb'
    if len(pieces) > 3:
        category = 'phrase'
    return category
