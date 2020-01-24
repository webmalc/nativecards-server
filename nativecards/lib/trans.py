"""
The translate module
"""
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests
from googletrans import Translator

from nativecards.lib.cache import cache_result
from nativecards.lib.settings import Chain, get_chain
from words.models import Word


class TranslationError(Exception):
    """
    The translations error class
    """


class Translate(Chain):
    """
    The base translation class
    """
    @property
    @abstractmethod
    def supported_languages(self) -> Optional[List[str]]:
        """
        Available languages (None - for all languages)
        """

    def check(self, **kwargs):
        """
        Check if the language is available
        """
        if not self.supported_languages:
            return True
        return kwargs.get('language') in self.supported_languages


class GoogleTrans(Translate):
    """
    The Google translate translation class
    """
    supported_languages = None
    languages_override = {'zh': 'zh-TW'}

    def get_result(self, **kwargs):
        """
        Get the translation
        """
        translator = Translator()
        language = kwargs.get('language')
        word = kwargs.get('word')
        language = self.languages_override.get(language, language)
        return [translator.translate(word, dest=language).text]


class Lingualeo(Translate):
    """
    The Lingualeo translation class
    """
    supported_languages = ['ru']
    url = 'https://api.lingualeo.com/gettranslates?port=1001&word='

    def get_result(self, **kwargs):
        word = kwargs.get('word')
        result = requests.get(self.url + word.lower())
        if result.status_code == 200:
            data = result.json()
            if 'error_msg' in data and data['error_msg']:
                return []
            entries = data['translate'][:3]
            translations = [v['value'] for v in entries]
            return translations
        return []


@dataclass
class TranaslationManager():
    """
    The translation manager
    """

    word: str
    language: str

    def _get_from_word(self) -> Optional[Dict[str, str]]:
        """
        Get translations from the word object
        """
        word = Word.objects.get_with_translation(self.word, self.language)
        if word:
            return {'translation': word.translations[self.language]}
        return None

    def _save_to_word(self, translation: str) -> None:
        """
        Save translation to the word object
        """
        Word.objects.create_or_update(
            self.word,
            translation=translation,
            language=self.language,
        )

    def _get_from_translator(self) -> Optional[Dict[str, str]]:
        """
        Get get translations from the translators
        """
        result = get_chain('TRANSLATORS').handle(
            word=self.word.lower(),
            language=self.language,
        )
        if result:
            translation = ', '.join(result)
            self._save_to_word(translation)
            return {'translation': translation}
        return None

    def translate(self) -> Optional[Dict[str, str]]:
        """
        Get the word translation
        """
        if not self.word:
            raise TranslationError('The word parameter not found.')
        if not self.language:
            raise TranslationError('The language parameter not found.')

        return self._get_from_word() or self._get_from_translator()


@cache_result('translation')
def translate(word: str, language: str) -> Optional[Dict[str, str]]:
    """
    Get the word translation
    """
    manager = TranaslationManager(word, language)
    try:
        return manager.translate()
    except TranslationError as error:
        return {'error': str(error)}
