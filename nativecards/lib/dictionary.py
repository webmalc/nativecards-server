"""
The dictionary module
"""
from typing import Optional

from django.conf import settings
from django.utils.module_loading import import_string

from nativecards.lib.cache import cache_result


@cache_result('definition')
def get_defenition(word) -> Optional[dict]:
    """
    Get the word's definition
    """
    if not word:
        return {'error': 'The word parameter not found.'}
    word = word.lower()
    for dictionary_class in settings.NC_DICTIONARIES:
        dictionary = import_string(dictionary_class)()
        result = dictionary.process(word.lower())
        if result and result.definition:
            return result.__dict__
    return None


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
