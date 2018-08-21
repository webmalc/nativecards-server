from abc import ABC, abstractmethod

import requests


class Translate(ABC):
    """
    Base translation class
    """

    @abstractmethod
    def translate(self, word: str) -> list:
        """
        Get the translation
        """
        pass


class Lingualeo(Translate):
    """
    Lingualeo translation class
    """
    URL = 'https://api.lingualeo.com/gettranslates?word='

    def translate(self, word: str) -> list:
        result = requests.get(self.URL + word)
        if result.status_code == 200:
            data = result.json()
            if 'error_msg' in data and data['error_msg']:
                return []
            entries = data['translate'][:3]
            translations = [v['value'] for v in entries]
            return translations
        return []


def translate(word) -> object:
    """
    Get the word translation
    """
    if not word:
        return {'error': 'The word parameter not found.'}
    trans = Lingualeo()
    return {'translation': ', '.join(trans.translate(word))}
