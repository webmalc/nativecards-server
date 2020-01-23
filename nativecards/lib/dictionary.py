"""
The dictionary module
"""
from typing import Dict, Optional

from django.apps import apps

from nativecards.lib.cache import cache_result
from nativecards.lib.settings import get_instances


class DictionaryError(Exception):
    """
    The dictionary error class
    """


class DictionaryManager():
    """
    The dictionary manager
    """

    word: str

    def __init__(self, word: str):
        self.word = word
        self.word_model = apps.get_model('words.Word')

    def _get_from_word(self) -> Optional[Dict[str, str]]:
        """
        Get synonyms and antonyms from the words object
        """
        word = self.word_model.objects.filter(word=self.word).exclude(
            definition__isnull=True).first()
        if word:
            return {
                'definition': word.definition,
                'examples': word.examples,
                'pronunciation': word.pronunciation,
                'transcription': word.transcription,
            }
        return None

    def _get_from_dictionary(self) -> Optional[Dict[str, str]]:
        """
        Get get definition from the dictionaries
        """
        for dictionary in get_instances('DICTIONARIES'):
            result = dictionary.process(self.word.lower())
            if result and result.definition:
                self.word_model.objects.create_or_update(
                    self.word,
                    definition=result,
                )
                return result.__dict__
        return None

    def get_definition(self) -> Optional[dict]:
        """
        Get the word's definition
        """
        if not self.word:
            raise DictionaryError('The word parameter not found.')
        self.word = self.word.lower()
        result = self._get_from_word()
        if result:
            return result
        return self._get_from_dictionary()


@cache_result('definition')
def get_definition(word) -> Optional[dict]:
    """
    Get the word's definition
    """
    manager = DictionaryManager(word)
    try:
        return manager.get_definition()
    except DictionaryError as error:
        return {'error': str(error)}


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
