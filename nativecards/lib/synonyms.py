"""
The synonyms module
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional

import requests
from django.conf import settings

from nativecards.lib.cache import cache_result
from nativecards.lib.dicts.base import DictionaryEntry
from nativecards.lib.settings import get_instances
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

    def get_synonyms(self, word: str) -> Optional[DictionaryEntry]:
        url = '{}/{}/{}/json'.format(self.url, self.key, word.lower())
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            entry = DictionaryEntry()
            for part_of_speach, keys in data.items():

                def get(
                        entry: DictionaryEntry,
                        key: str,
                        name: str,
                        keys,
                        part_of_speach,
                ) -> DictionaryEntry:
                    if key in keys:
                        for value in keys[key][:5]:
                            entry.add_data_entry(name, value, part_of_speach)
                    return entry

                entry = get(entry, 'syn', 'synonyms', keys, part_of_speach)
                entry = get(entry, 'ant', 'antonyms', keys, part_of_speach)

            entry.process_data()
            return entry
        return None


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
            return DictionaryEntry(
                synonyms=word.synonyms,
                antonyms=word.antonyms,
            )
        return None

    def _get_from_thesaurus(self) -> Optional[DictionaryEntry]:
        """
        Get synonyms and antonyms from the thesauruses
        """
        for thesaurus in get_instances('THESAURI'):
            result = thesaurus.get_synonyms(self.word.lower())
            if result:
                Word.objects.create_or_update(
                    self.word,
                    synonyms=result.synonyms,
                    antonyms=result.antonyms,
                )
                return result
        return None

    def get_entry(self) -> Optional[Dict[str, str]]:
        """
        Get the word's synonyms
        """
        if not self.word:
            raise ThesaurusError('The word parameter not found.')
        result = self._get_from_word()
        if result:
            return result.__dict__
        result = self._get_from_thesaurus()
        if result:
            return result.__dict__
        return None


@cache_result('synonyms')
def get_synonyms(word: str) -> Optional[Dict[str, str]]:
    """
    Get the word's synonyms
    """

    manager = ThesaurusManager(word)
    try:
        return manager.get_entry()
    except ThesaurusError as error:
        return {'error': str(error)}
