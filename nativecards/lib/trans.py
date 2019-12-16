"""
The translate module
"""
from abc import ABC, abstractmethod
from typing import Optional

import requests
from django.conf import settings
from django.utils.module_loading import import_string
from googletrans import Translator

from nativecards.lib.cache import cache_result


class Translate(ABC):
    """
    The base translation class
    """

    @property
    @abstractmethod
    def supported_languages(self):
        """
        Available languages (None - for all languages)
        """

    def check_language(self, language: str):
        """
        Check if the language is available
        """
        if not self.supported_languages:
            return True
        return language in self.supported_languages

    @abstractmethod
    def translate(self, word: str, language: str) -> list:
        """
        Get the translation
        """


class GoogleTrans(Translate):
    """
    The Google translate translation class
    """
    supported_languages = None
    languages_override = {'zh': 'zh-TW'}

    def translate(self, word: str, language: str) -> list:
        """
        Get the translation
        """
        translator = Translator()
        language = self.languages_override.get(language, language)
        return [translator.translate(word, dest=language).text]


class Lingualeo(Translate):
    """
    The Lingualeo translation class
    """
    supported_languages = ['ru']
    url = 'https://api.lingualeo.com/gettranslates?port=1001&word='

    def translate(self, word: str, language: str) -> list:
        result = requests.get(self.url + word.lower())
        if result.status_code == 200:
            data = result.json()
            if 'error_msg' in data and data['error_msg']:
                return []
            entries = data['translate'][:3]
            translations = [v['value'] for v in entries]
            return translations
        return []


@cache_result('translation')
def translate(word: str, language: Optional[str] = None) -> Optional[dict]:
    """
    Get the word translation
    """
    if not word:
        return {'error': 'The word parameter not found.'}
    if not language:
        return {'error': 'The language parameter not found.'}

    for translator_class in settings.NC_TRANSLATORS:
        translator = import_string(translator_class)()
        if translator.check_language(language):
            result = translator.translate(word.lower(), language)
            if result:
                return {'translation': ', '.join(result)}

    return None
