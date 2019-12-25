"""
The synonyms module
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings

from nativecards.lib.cache import cache_result
from nativecards.lib.dicts.base import DictionaryEntry
from words.models import Word


class ThesaurusError(Exception):
    """
    The thesaurus error class
    """


class Thesaurus(ABC):
    """
    Base thesaurus class
    """
    @abstractmethod
    def get_synonyms(self, word: str) -> Optional[DictionaryEntry]:
        """
        Get the synonyms
        """


class BigHugeThesaurus(Thesaurus):
    """
    Bighugelabs thesaurus
    """

    url = 'http://words.bighugelabs.com/api/2'
    key = settings.NC_BIGHUGELABS_KEY

    def get_synonyms(self, word: str) -> DictionaryEntry:
        url = '{}/{}/{}/json'.format(self.url, self.key, word.lower())
        response = requests.get(url)
        synonyms = antonyms = ''
        if response.status_code == 200:
            data = response.json()
            for val, keys in data.items():

                def get(key: str, keys, val) -> str:
                    result = ''
                    if key in keys:
                        result = '{}: {}\n\n'.format(
                            val,
                            ', '.join(keys[key][:5]),
                        )
                    return result

                synonyms += get('syn', keys, val)
                antonyms += get('ant', keys, val)

        return DictionaryEntry(synonyms=synonyms, antonyms=antonyms)


@dataclass
class ThesaurusManager():
    """
    The thesaurus manager
    """

    word: str

    def _get_from_word(self) -> Optional[DictionaryEntry]:
        """
        Get synonyms and antonyms from the words object
        """
        word = Word.objects.filter(word=self.word).exclude(
            synonyms__isnull=True,
            antonyms__isnull=True,
        ).first()
        if word:
            return DictionaryEntry(synonyms=word.synonyms,
                                   antonyms=word.antonyms)
        return None

    def _get_from_thesaurus(self) -> DictionaryEntry:
        """
        Get synonyms and antonyms from the thesauruses
        """
        thesaurus = BigHugeThesaurus()
        result = thesaurus.get_synonyms(self.word.lower())
        Word.objects.create_or_update(
            self.word,
            synonyms=result.synonyms,
            antonyms=result.antonyms,
        )
        return result

    def get_entry(self) -> dict:
        """
        Get the word's synonyms
        """
        if not self.word:
            raise ThesaurusError('The word parameter not found.')
        result = self._get_from_word()
        if result:
            return result.__dict__
        return self._get_from_thesaurus().__dict__


@cache_result('synonyms')
def get_synonyms(word: str) -> dict:
    """
    Get the word's synonyms
    """

    manager = ThesaurusManager(word)
    try:
        return manager.get_entry()
    except ThesaurusError as error:
        return {'error': str(error)}
