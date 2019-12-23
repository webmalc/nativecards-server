"""
The dictionary module
"""
import json
from typing import Optional

from nativecards.lib.dicts.base import Dictionary, DictionaryEntry


class WordsApi(Dictionary):
    """
    The WordsApi dictionary
    """

    def get_json(self, word: str) -> str:
        """
        Get words JSON
        """

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
