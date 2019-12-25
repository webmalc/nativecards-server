"""
The dictionary module
"""
from abc import ABC, abstractmethod
from typing import Optional

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

    def __init__(
            self,
            definition: Optional[str] = None,
            examples: Optional[str] = None,
            pronunciation: Optional[str] = None,
            transcription: Optional[str] = None,
            synonyms: Optional[str] = None,
            antonyms: Optional[str] = None,
    ) -> None:
        self.pronunciation = pronunciation or None
        self.examples = examples or None
        self.definition = definition or None
        self.transcription = transcription or None
        self.synonyms = synonyms or None
        self.antonyms = antonyms or None
        for key, entry in self.__dict__.items():
            if isinstance(entry, str):
                self.__dict__[key] = entry.strip(', \n')


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
