"""
The synonyms module
"""

from abc import ABC, abstractmethod

import requests
from django.conf import settings

from nativecards.lib.cache import cache_result


class Thesaurus(ABC):
    """
    Base thesaurus class
    """

    @abstractmethod
    def get_synonyms(self, word: str):
        """
        Get the synonyms
        """


class BigHugeThesaurus(Thesaurus):
    """
    Bighugelabs thesaurus
    """

    url = 'http://words.bighugelabs.com/api/2'
    key = settings.NC_BIGHUGELABS_KEY

    def get_synonyms(self, word: str):
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

        return {'synonyms': synonyms, 'antonyms': antonyms}


@cache_result('synonyms')
def get_synonyms(word) -> dict:
    """
    Get the word's synonyms
    """
    if not word:
        return {'error': 'The word parameter not found.'}
    thesaurus = BigHugeThesaurus()
    return thesaurus.get_synonyms(word.lower())
