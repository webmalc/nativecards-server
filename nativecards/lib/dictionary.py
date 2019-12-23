"""
The dictionary module
"""
from typing import Dict, Optional

from django.apps import apps
from django.conf import settings
from django.utils.module_loading import import_string

from nativecards.lib.cache import cache_result


def _get_from_word(word: str) -> Optional[Dict[str, str]]:
    """
    Get synonyms and antonyms from the words object
    """
    word_model = apps.get_model('words.Word')
    word = word_model.objects.filter(word=word).exclude(
        definition__isnull=True, ).first()
    if word:
        return {
            'definition': word.definition,
            'examples': word.examples,
            'pronunciation': word.pronunciation,
            'transcription': word.transcription,
        }
    return None


def _get_from_dictionary(word: str) -> Optional[Dict[str, str]]:
    """
    Get get definition from the dictionaries
    """
    word_model = apps.get_model('words.Word')
    for dictionary_class in settings.NC_DICTIONARIES:
        dictionary = import_string(dictionary_class)()
        result = dictionary.process(word.lower())
        if result and result.definition:
            word_model = apps.get_model('words.Word')
            word_model.objects.create_or_update(word, definition=result)
            return result.__dict__
    return None


@cache_result('definition')
def get_definition(word) -> Optional[dict]:
    """
    Get the word's definition
    """
    if not word:
        return {'error': 'The word parameter not found.'}
    word = word.lower()
    result = _get_from_word(word)
    if result:
        return result
    return _get_from_dictionary(word)


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
