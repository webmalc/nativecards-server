"""
The dictionary module
"""
import json
from collections import defaultdict
from typing import Dict, Optional

import requests
from django.conf import settings

from nativecards.lib.cache import save_result
from nativecards.lib.dicts.base import Dictionary, DictionaryEntry
from nativecards.lib.synonyms import Thesaurus


class WordsApi(Dictionary, Thesaurus):
    """
    The WordsApi dictionary
    """
    url: str = 'https://wordsapiv1.p.rapidapi.com/words/{}'
    headers: Dict[str, str] = {
        'x-rapidapi-host': 'wordsapiv1.p.rapidapi.com',
        'x-rapidapi-key': settings.NC_RAPIDAPI_KEY
    }

    @save_result('wordsapi/{}.json')
    def _get_json(self, word: str) -> Optional[str]:
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

    def _get_data(self, word: str) -> Optional[dict]:
        """
        Get data from JSON
        """
        try:
            data = json.loads(self._get_json(word))
        except (json.JSONDecodeError, TypeError):
            data = None

        return data

    @staticmethod
    def _process_entry(
            result: dict,
            data: dict,
            key: str,
            delimiter: str = '\n\n',
    ) -> dict:
        """
        Extract data from a result row
        """
        entry = data.get(key)
        if entry:
            result[key] += '{}{}'.format(delimiter.join(entry), delimiter)
        return result

    def get_synonyms(self, word: str) -> Optional[DictionaryEntry]:
        """
        Get the synonyms
        """
        return self.get_entry(word)

    def get_entry(self, word: str) -> Optional[DictionaryEntry]:
        """
        Get the word or phrase entry
        """
        data = self._get_data(word)
        if not data:
            return None
        results = data.get('results')
        if not results:
            return None
        entry_data = defaultdict(str)
        for result in results:
            entry_data['definition'] += '{}\n\n'.format(
                result.get('definition'))
            entry_data = self._process_entry(entry_data, result, 'examples')
            entry_data = self._process_entry(
                entry_data,
                result,
                'synonyms',
                ', ',
            )
            entry_data = self._process_entry(
                entry_data,
                result,
                'antonyms',
                ', ',
            )

        entry_data['transcription'] = data.get('pronunciation', {}).get('all')
        entry = DictionaryEntry(**entry_data)

        return entry
