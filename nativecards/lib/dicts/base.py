"""
The dictionary module
"""
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, Optional

from django.template.loader import render_to_string

from nativecards.lib.audio import get_audio


class DictionaryEntry():
    """
    The definition entry class
    """
    pronunciation: Optional[str] = None
    examples: Optional[str] = None
    definition: Optional[str] = None
    transcription: Optional[str] = None
    synonyms: Optional[str] = None
    antonyms: Optional[str] = None
    data: Dict[str, str] = None

    def add_data_entry(self, name: str, value: str, part_of_speach: str):
        """
        Add an data entry
        """
        if part_of_speach not in self.data[name]:
            self.data[name][part_of_speach] = []
        self.data[name][part_of_speach].append(value)

    def process_data(self):
        """
        Render the data
        """
        for name in ('definition', 'examples', 'synonyms', 'antonyms'):
            data = self.data[name]
            if data:
                setattr(
                    self,
                    name,
                    render_to_string(
                        'dicts/{}.md'.format(name),
                        {'entries': dict(data)},
                    ),
                )
        self._clean_data()

    def _clean_data(self):
        """
        Clean the processed data
        """
        for key, entry in self.__dict__.items():
            if isinstance(entry, str):
                self.__dict__[key] = entry.strip(', \n')

    def __init__(
            self,
            definition: Optional[str] = None,
            examples: Optional[str] = None,
            pronunciation: Optional[str] = None,
            transcription: Optional[str] = None,
            synonyms: Optional[str] = None,
            antonyms: Optional[str] = None,
    ) -> None:
        self.data = defaultdict(dict)
        self.pronunciation = pronunciation or None
        self.examples = examples or None
        self.definition = definition or None
        self.transcription = transcription or None
        self.synonyms = synonyms or None
        self.antonyms = antonyms or None
        self._clean_data()


class Dictionary(ABC):
    """
    Base dictionary class
    """
    @abstractmethod
    def get_entry(self, word: str) -> Optional[DictionaryEntry]:
        """
        Get the word or phrase entry
        """

    def process(self, word: str) -> Optional[DictionaryEntry]:
        """
        Get the definition
        """
        info = self.get_entry(word)
        if info and not info.pronunciation:
            info.pronunciation = get_audio(word)
        return info
