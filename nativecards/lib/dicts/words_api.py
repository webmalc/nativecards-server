"""
The dictionary module
"""
import json
from typing import Dict, Optional

import requests
from django.conf import settings

from nativecards.lib.cache import save_result
from nativecards.lib.dicts.models import DictionaryEntry
from nativecards.lib.settings import Chain


class WordsApi(Chain):
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
            data: dict,
            entry: DictionaryEntry,
            key: str,
            part_of_speach: str = '',
    ) -> DictionaryEntry:
        """
        Extract data from a result row
        """
        entries = data.get(key)
        if entries:
            for value in entries:
                entry.add_data_entry(key, value, part_of_speach)
        return entry

    def get_result(self, **kwargs) -> Optional[DictionaryEntry]:
        """
        Get the word or phrase entry
        """
        word = str(kwargs.get('word'))
        data = self._get_data(word)
        if not data:
            return None
        results = data.get('results')
        if not results:
            return None
        entry = DictionaryEntry()

        for result in results:
            part_of_speach = result.get('partOfSpeech')
            entry.add_data_entry(
                'definition',
                result.get('definition'),
                part_of_speach,
            )
            entry = self._process_entry(
                result,
                entry,
                'examples',
                part_of_speach=part_of_speach,
            )
            entry = self._process_entry(
                result,
                entry,
                'synonyms',
                part_of_speach=part_of_speach,
            )
            entry = self._process_entry(
                result,
                entry,
                'antonyms',
                part_of_speach=part_of_speach,
            )
        entry.transcription = data.get('pronunciation', {}).get('all')
        entry.process_data()

        return entry
