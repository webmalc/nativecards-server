"""
The dictionary module
"""
import re
from abc import ABC, abstractmethod
from typing import List
from xml.etree import ElementTree

import requests
from django.conf import settings

from nativecards.lib.cache import cache_result  # pylint: disable=import-error


class Thesaurus(ABC):
    """
    Base thesaurus class
    """

    @abstractmethod
    def get_synonyms(self, word: str):
        """
        Get the synonyms
        """


class Dictionary(ABC):
    """
    Base dictionary class
    """

    @abstractmethod
    def get_defenition(self, word: str):
        """
        Get the definition
        """


class WebsterLearners(Dictionary):
    """
    Webster learners dictionary
    """
    url = 'https://www.dictionaryapi.com/api/v1/references/learners/xml/'
    audio_url = 'https://media.merriam-webster.com/soundc11/'
    key = settings.NC_WEBSTER_LEARNERS_KEY

    def _get_audio(self, tree) -> List[str]:
        data = []
        for element in tree.iter('wav'):
            filename = element.text
            folder = 'h'
            if filename[:3] == 'bix':
                folder = 'bix'
            elif filename[:2] == 'gg':
                folder = 'gg'
            else:
                folder = filename[0]
            file_url = '{}{}/{}'.format(self.audio_url, folder, filename)
            data.append(file_url)
        return data

    @staticmethod
    def _get_definition(tree) -> str:
        definition = ''
        entry = tree.find('entry')
        if not entry:
            return ''
        for element in entry.find('def').iter('dt'):
            text = element.text if element.text else ''
            sx_element = element.find('sx')
            un_element = element.find('un')
            if hasattr(sx_element, 'text'):
                text += sx_element.text
            if hasattr(un_element, 'text'):
                text += un_element.text
            text = text.replace(':', '')
            if text:
                definition += '{}\n\n'.format(text)
        return definition

    @staticmethod
    def _get_transcription(tree) -> str:
        result = getattr(tree.find('./entry/pr'), 'text', None)
        if not result:
            result = getattr(tree.find('./entry/vr/pr'), 'text', '')
        return result

    @staticmethod
    def _get_examples(tree) -> str:
        examples = ''
        entry = tree.find('entry')
        if not entry:
            return ''
        for element in entry.find('def').iter('vi'):
            text = ElementTree.tostring(element).decode('utf-8')
            text = text.replace('</vi>', '\n').replace('<vi>', '')
            text = re.sub(r'</?(it|phrase){1}>', '*', text)
            if text:
                examples += '{}\n'.format(text)
        return examples

    def get_defenition(self, word: str):
        """
        Returns the word defenition
        """
        url = '{}{}?key={}'.format(self.url, word, self.key)
        response = requests.get(url)
        if response.status_code == 200:
            audio = []  # type: List[str]
            examples = definition = transcription = None
            try:
                tree = ElementTree.fromstring(response.text)
                audio = self._get_audio(tree)
                examples = self._get_examples(tree)
                definition = self._get_definition(tree)
                transcription = self._get_transcription(tree)
            except ElementTree.ParseError:
                pass

            result = {
                'pronunciation': audio[0] if audio else None,
                'examples': examples or None,
                'definition': definition or None,
                'transcription': transcription or None
            }
            return result

        return None


class BigHugeThesaurus(Thesaurus):
    """
    Bighugelabs thesaurus
    """

    url = 'http://words.bighugelabs.com/api/2'
    key = settings.NC_BIGHUGELABS_KEY

    def get_synonyms(self, word: str):
        url = '{}/{}/{}/json'.format(self.url, self.key, word.lower())
        response = requests.get(url)
        synonyms = antonyms = ''
        if response.status_code == 200:
            data = response.json()
            for val, keys in data.items():

                def get(key: str, keys, val) -> str:
                    result = ''
                    if key in keys:
                        result = '{}: {}\n\n'.format(
                            val,
                            ', '.join(keys[key][:5]),
                        )
                    return result

                synonyms += get('syn', keys, val)
                antonyms += get('ant', keys, val)

        return {'synonyms': synonyms, 'antonyms': antonyms}


@cache_result('definition')
def get_defenition(word) -> object:
    """
    Get the word's definition
    """
    if not word:
        return {'error': 'The word parameter not found.'}
    dictionary = WebsterLearners()
    return dictionary.get_defenition(word)


@cache_result('synonyms')
def get_synonyms(word) -> object:
    """
    Get the word's synonyms
    """
    if not word:
        return {'error': 'The word parameter not found.'}
    thesaurus = BigHugeThesaurus()
    return thesaurus.get_synonyms(word)
