"""
The translate module
"""
from abc import ABC, abstractmethod

import requests

from nativecards.lib.cache import cache_result


class Translate(ABC):
    """
    The base translation class
    """

    @abstractmethod
    def translate(self, word: str) -> list:
        """
        Get the translation
        """


class Lingualeo(Translate):
    """
    The Lingualeo translation class
    """
    url = 'https://api.lingualeo.com/gettranslates?port=1001&word='

    def translate(self, word: str) -> list:
        result = requests.get(self.url + word.lower())
        if result.status_code == 200:
            data = result.json()
            if 'error_msg' in data and data['error_msg']:
                return []
            entries = data['translate'][:3]
            translations = [v['value'] for v in entries]
            return translations
        return []


@cache_result('translation')
def translate(word) -> object:
    """
    Get the word translation
    """
    if not word:
        return {'error': 'The word parameter not found.'}

    trans = Lingualeo()
    return {'translation': ', '.join(trans.translate(word.lower()))}
