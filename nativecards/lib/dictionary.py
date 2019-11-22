import re
from abc import ABC, abstractmethod
from typing import List
from xml.etree import ElementTree

import requests
from django.conf import settings

from nativecards.lib.cache import cache_result


class Thesaurus(ABC):
    """
    Base thesaurus class
    """

    @abstractmethod
    def get_synonyms(self, word: str):
        """
        Get the synonyms
        """
        pass


class Dictionary(ABC):
    """
    Base dictionary class
    """

    @abstractmethod
    def definition(self, word: str):
        """
        Get the definition
        """
        pass


class WebsterLearners(Dictionary):
    """
    Webster learners dictionary
    """
    url = 'https://www.dictionaryapi.com/api/v1/references/learners/xml/'
    audio_url = 'https://media.merriam-webster.com/soundc11/'
    key = settings.NC_WEBSTER_LEARNERS_KEY

    def _get_audio(self, tree) -> List[str]:
        data = []
        for el in tree.iter('wav'):
            filename = el.text
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

    def _get_definition(self, tree) -> str:
        definition = ''
        entry = tree.find('entry')
        if not entry:
            return ''
        for el in entry.find('def').iter('dt'):
            text = el.text if el.text else ''
            sx = el.find('sx')
            un = el.find('un')
            if hasattr(sx, 'text'):
                text += sx.text
            if hasattr(un, 'text'):
                text += un.text
            text = text.replace(':', '')
            if text:
                definition += '{}\n\n'.format(text)
        return definition

    def _get_transcription(self, tree) -> str:
        result = getattr(tree.find('./entry/pr'), 'text', None)
        if not result:
            result = getattr(tree.find('./entry/vr/pr'), 'text', '')
        return result

    def _get_examples(self, tree) -> str:
        examples = ''
        entry = tree.find('entry')
        if not entry:
            return ''
        for el in entry.find('def').iter('vi'):
            text = ElementTree.tostring(el).decode('utf-8')
            text = text.replace('</vi>', '\n').replace('<vi>', '')
            text = re.sub(r'</?(it|phrase){1}>', '*', text)
            if text:
                examples += '{}\n'.format(text)
        return examples

    def definition(self, word: str):
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
                'pronunciation': audio[0] if len(audio) else None,
                'examples': examples or None,
                'definition': definition or None,
                'transcription': transcription or None
            }
            return result

        return None


class Oxford(Dictionary):
    """
    Oxford dictionary
    """
    url = 'https://od-api.oxforddictionaries.com/api/v1'
    id = settings.NC_OXFORD_ID
    key = settings.NC_OXFORD_KEY

    def definition(self, word: str):
        url = self.url + '/entries/en/' + word.lower(
        ) + '/definitions;examples;pronunciations'
        result = requests.get(url,
                              headers={
                                  'app_id': self.id,
                                  'app_key': self.key
                              })
        if result.status_code == 200:
            data = result.json()
            # TODO: complete !!!
            return data

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
            for s, k in data.items():

                def get(key: str) -> str:
                    result = ''
                    if key in k:
                        result = '{}: {}\n\n'.format(s, ', '.join(k[key][:5]))
                    return result

                synonyms += get('syn')
                antonyms += get('ant')

        return {'synonyms': synonyms, 'antonyms': antonyms}


@cache_result('definition')
def definition(word) -> object:
    """
    Get the word's definition
    """
    if not word:
        return {'error': 'The word parameter not found.'}
    dictionary = WebsterLearners()
    return dictionary.definition(word)


@cache_result('synonyms')
def get_synonyms(word) -> object:
    """
    Get the word's synonyms
    """
    if not word:
        return {'error': 'The word parameter not found.'}
    thesaurus = BigHugeThesaurus()
    return thesaurus.get_synonyms(word)
