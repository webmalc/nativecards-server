"""
The synonyms module
"""
from typing import Dict, List, Optional

import requests
from django.conf import settings
from django.db.models.query import QuerySet

from nativecards.lib.cache import cache_result
from nativecards.lib.settings import Chain
from words.models import Word

from .dicts.models import BaseManager, DictionaryEntry, manager_runner


class BigHugeThesaurus(Chain):
    """
    Bighugelabs thesaurus
    """

    url = 'http://words.bighugelabs.com/api/2'
    key = settings.NC_BIGHUGELABS_KEY

    def get_result(self, **kwargs):
        word = kwargs.get('word')
        url = '{}/{}/{}/json'.format(self.url, self.key, word.lower())
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            entry = DictionaryEntry()
            for part_of_speech, keys in data.items():

                def get(
                        entry: DictionaryEntry,
                        key: str,
                        name: str,
                        keys,
                        part_of_speech,
                ) -> DictionaryEntry:
                    if key in keys:
                        for value in keys[key][:5]:
                            entry.add_data_entry(name, value, part_of_speech)
                    return entry

                entry = get(entry, 'syn', 'synonyms', keys, part_of_speech)
                entry = get(entry, 'ant', 'antonyms', keys, part_of_speech)

            entry.process_data()
            return entry
        return None


class ThesaurusManager(BaseManager):
    """
    The thesaurus manager
    """
    settings_key: str = 'THESAURI'
    word_fields: List[str] = ['synonyms', 'antonyms']
    word_query: QuerySet = Word.objects.get_with_synonyms


@cache_result('synonyms')
def get_synonyms(word: str) -> Optional[Dict[str, str]]:
    """
    Get the word's synonyms
    """
    return manager_runner(word, ThesaurusManager)
