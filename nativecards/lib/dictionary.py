from abc import ABC, abstractmethod

import requests
from django.conf import settings


class Dictionary(ABC):
    """
    Base dictionary class
    """

    @abstractmethod
    def definition(self, word: str):
        """
        Get the definition
        """
        pass


class Oxford(Dictionary):
    """
    Oxford dictionary
    """
    url = 'https://od-api.oxforddictionaries.com/api/v1'
    id = settings.NC_OXFORD_ID
    key = settings.NC_OXFORD_KEY

    def definition(self, word: str) -> object:
        url = self.url + '/entries/en/' + word.lower(
        ) + '/definitions;examples;pronunciations'
        result = requests.get(
            url, headers={
                'app_id': self.id,
                'app_key': self.key
            })
        if result.status_code == 200:
            data = result.json()
            return data

        return None


def definition(word) -> object:
    """
    Get the word definition
    """
    if not word:
        return {'error': 'The word parameter not found.'}
    dictionary = Oxford()
    data = dictionary.definition(word)
    return data
