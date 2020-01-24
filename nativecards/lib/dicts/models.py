"""
The dictionary module
"""
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

from django.apps import apps
from django.db.models.query import QuerySet
from django.template.loader import render_to_string

from ..settings import get_chain


class DictionaryError(Exception):
    """
    The dictionary error class
    """


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
    data: Dict[str, Any] = {}

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


class BaseManager(ABC):
    """
    The base dictionary manager
    """

    word: str

    @property
    @abstractmethod
    def settings_key(self) -> str:
        """
        Chain settings key
        """

    @property
    @abstractmethod
    def word_fields(self) -> List[str]:
        """
        Words fields
        """

    @property
    @abstractmethod
    def word_query(self) -> QuerySet:
        """
        Words query
        """

    def __init__(self, word: str):
        self.word = word
        self.word_model = apps.get_model('words.Word')

    def _get_from_word(self) -> Optional[Dict[str, str]]:
        """
        Get synonyms and antonyms from the words object
        """
        word = self.word_query(self.word)
        if word:
            return {f: getattr(word, f) for f in self.word_fields}
        return None

    def _save_to_word(self, result: DictionaryEntry) -> None:
        """
        Save results to the word object
        """
        self.word_model.objects.create_or_update(self.word, entry=result)

    def get_entry(self) -> Optional[dict]:
        """
        Get the word's definition
        """
        if not self.word:
            raise DictionaryError('The word parameter not found.')
        return self._get_from_word() or self._get_from_dictionary()

    @staticmethod
    def is_result_valid(result: Optional[DictionaryEntry]) -> bool:
        """
        Checks result
        """
        return bool(result)

    def process_result(self, result: DictionaryEntry) -> DictionaryEntry:
        """
        Processes result
        """
        # pylint: disable=no-self-use
        return result

    def _get_from_dictionary(self) -> Optional[Dict[str, str]]:
        """
        Get get definition from the dictionaries
        """
        result = get_chain(self.settings_key).handle(word=self.word)

        if not self.is_result_valid(result):
            return None

        result = self.process_result(result)
        self._save_to_word(result)

        return result.__dict__


def manager_runner(
        word: str,
        manager_cls: Callable[[str], BaseManager],
) -> Optional[dict]:
    """
    Gets results from a manager
    """
    manager = manager_cls(word.lower())
    try:
        return manager.get_entry()
    except DictionaryError as error:
        return {'error': str(error)}
