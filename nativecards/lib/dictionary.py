from abc import ABC, abstractmethod
from xml.etree import ElementTree

import requests
from django.conf import settings


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

    def _get_audio(self, tree) -> list:
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
                definition += '<p>{}</p>\n'.format(text)
        return definition

    def _get_examples(self, tree) -> str:
        examples = ''
        entry = tree.find('entry')
        if not entry:
            return ''
        for el in entry.find('def').iter('vi'):
            text = ElementTree.tostring(el).decode('utf-8')
            text = text.replace('vi>', 'p>').replace('it>', 'i>')
            if text:
                examples += '{}\n'.format(text)
        return examples

    def definition(self, word: str):
        url = '{}{}?key={}'.format(self.url, word, self.key)
        response = requests.get(url)
        if response.status_code == 200:
            tree = ElementTree.fromstring(response.text)
            audio = self._get_audio(tree)
            examples = self._get_examples(tree)
            definition = self._get_definition(tree)

            result = {
                'pronunciation': audio[0] if len(audio) else None,
                'examples': examples,
                'definition': definition
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
        result = requests.get(
            url, headers={
                'app_id': self.id,
                'app_key': self.key
            })
        if result.status_code == 200:
            data = result.json()
            # TODO: complete !!!
            return data

        return None


def definition(word) -> object:
    """
    Get the word definition
    """
    if not word:
        return {'error': 'The word parameter not found.'}
    dictionary = WebsterLearners()
    return dictionary.definition(word)
