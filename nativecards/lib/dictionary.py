"""
The dictionary module
"""
import re
from abc import ABC, abstractmethod
from typing import List
from xml.etree import ElementTree

import requests
from django.conf import settings

from nativecards.lib.audio import get_audio
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
    def get_entry(self, word: str) -> dict:
        """
        Get the word or phrase entry
        """

    def process(self, word: str) -> dict:
        """
        Get the definition
        """
        info = self.get_entry(word)
        if info and 'pronunciation' in info and not info['pronunciation']:
            info['pronunciation'] = get_audio(word)
        return info


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
    def _get_phrasal_verb_definition(root) -> str:
        """
        Get definition of the phrasal verb
        """
        definition = ''
        for element in root.iter('dt'):
            text = element.text if element.text else ''
            text = text.replace(':', '')
            if text:
                definition += '{}\n\n'.format(text)
        return definition

    @staticmethod
    def _get_phrasal_verb_examples(root) -> str:
        """
        Get examples for the phrasal verb
        """
        examples = ''
        for element in root.iter('vi'):
            text = ElementTree.tostring(element).decode('utf-8')
            text = re.sub(r'</?(it|phrase){1}>', '*', text)
            if text:
                examples += '{}\n\n'.format(text)
        return examples

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

    def _get_word_info(self, tree):
        """
        Returns the word information
        """
        audio = []  # type: List[str]
        examples = definition = transcription = None
        audio = self._get_audio(tree)
        examples = self._get_examples(tree)
        definition = self._get_definition(tree)
        transcription = self._get_transcription(tree)

        return {
            'pronunciation': audio[0] if audio else None,
            'examples': examples or None,
            'definition': definition or None,
            'transcription': transcription or None
        }

    def _get_phrasal_verb_info(self, tree, word: str):
        """
        Returns the phrasal verb word information
        """
        root = tree.find(".//dre[.='{}']/..".format(word))
        examples = definition = None
        if root:
            definition = self._get_phrasal_verb_definition(root)
            examples = self._get_phrasal_verb_examples(root)
        return {
            'pronunciation': None,
            'examples': examples or None,
            'definition': definition or None,
            'transcription': None
        }

    def get_entry(self, word: str):
        """
        Returns the word or phrase entry
        """
        url = '{}{}?key={}'.format(self.url, word, self.key)
        response = requests.get(url)
        if response.status_code == 200:
            try:
                tree = ElementTree.fromstring(response.text)
            except ElementTree.ParseError:
                return None
            category = guess_category(word)
            if category == 'phrasal_verb':
                return self._get_phrasal_verb_info(tree, word)
            return self._get_word_info(tree)

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
    return dictionary.process(word.lower())


@cache_result('synonyms')
def get_synonyms(word) -> object:
    """
    Get the word's synonyms
    """
    if not word:
        return {'error': 'The word parameter not found.'}
    thesaurus = BigHugeThesaurus()
    return thesaurus.get_synonyms(word.lower())


def guess_category(word: str) -> str:
    """
    Try to guess the word category
    """
    pieces = word.split(' ')
    category = 'word'
    if 1 < len(pieces) <= 3:
        category = 'phrasal_verb'
    if len(pieces) > 3:
        category = 'phrase'
    return category
