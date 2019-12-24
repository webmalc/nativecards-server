"""
The dictionary module
"""
import json
from typing import Dict, Optional

import requests
from django.conf import settings

from nativecards.lib.cache import save_result
from nativecards.lib.dicts.base import Dictionary, DictionaryEntry


class WordsApi(Dictionary):
    """
    The WordsApi dictionary
    """
    url: str = 'https://wordsapiv1.p.rapidapi.com/words/{}'
    headers: Dict[str, str] = {
        'x-rapidapi-host': 'wordsapiv1.p.rapidapi.com',
        'x-rapidapi-key': settings.NC_RAPIDAPI_KEY
    }

    @save_result('wordsapi/{}.json')
    def get_json(self, word: str) -> Optional[str]:
        """
        Get words JSON
        """
        response = requests.get(
            self.url.format(word),
            headers=self.headers,
        )
        if response.status_code == 200:
            return response.text
        return None

    def get_data(self, word: str) -> Optional[dict]:
        """
        Get data from JSON
        """
        try:
            data = json.loads(self.get_json(word))
        except json.JSONDecodeError:
            data = None

        return data

    def get_entry(self, word: str) -> Optional[DictionaryEntry]:
        """
        Get the word or phrase entry
        """
