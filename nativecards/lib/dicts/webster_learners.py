"""
The dictionary module
"""
import re
import shutil
from tempfile import NamedTemporaryFile
from typing import List, Optional
from xml.etree import ElementTree

import requests
from django.conf import settings
from django.core.files.storage import default_storage

from nativecards.lib.audio import (check_audio_path, get_audio_filename,
                                   get_audio_url)
from nativecards.lib.cache import save_result
from nativecards.lib.dictionary import guess_category
from nativecards.lib.dicts.models import DictionaryEntry
from nativecards.lib.settings import Chain


class WebsterLearners(Chain):
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
    def _get_definition(tree, entry: DictionaryEntry) -> DictionaryEntry:
        for value in tree.findall('entry'):
            part_of_speech = getattr(value.find('fl'), 'text', '-')
            def_element = value.find('def')
            if not def_element:
                continue
            for element in def_element.iter('dt'):
                text = element.text if element.text else ''
                sx_element = element.find('sx')
                un_element = element.find('un')
                if hasattr(sx_element, 'text'):
                    text += sx_element.text
                if hasattr(un_element, 'text'):
                    text += un_element.text
                text = text.replace(':', '')
                if text:
                    entry.add_data_entry(
                        'definition',
                        text.strip(' \n'),
                        part_of_speech,
                    )

        return entry

    @staticmethod
    def _get_phrasal_verb_definition(root) -> str:
        """
        Get definition of the phrasal verb
        """
        definition = ''
        for element in root.iter('dt'):
            text = element.text if element.text else ''
            text = text.replace(':', '')
            if not text:
                text = getattr(element.find('sx'), 'text', '')
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
            text = re.sub(r'</?(it|phrase|vi){1}>', '*', text)
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
    def _get_examples(tree, entry: DictionaryEntry) -> DictionaryEntry:
        for value in tree.findall('entry'):
            part_of_speech = getattr(value.find('fl'), 'text', '-')
            def_element = value.find('def')
            if not def_element:
                continue
            for element in def_element.iter('vi'):
                text = ElementTree.tostring(element).decode('utf-8')
                text = text.replace('</vi>', '\n').replace('<vi>', '')
                text = re.sub(r'</?(it|phrase){1}>', '*', text)
                if text:
                    entry.add_data_entry(
                        'examples',
                        text.strip(' \n'),
                        part_of_speech,
                    )
        return entry

    @staticmethod
    def _save_audio(audio: List[str], word: str) -> Optional[str]:
        """
        Save an audio to the server and return the result URL
        """
        audio_url = audio[0] if audio else None
        if not audio_url:
            return None

        filename = get_audio_filename(word, 'wav')
        url = get_audio_url(filename)
        if not check_audio_path(filename):
            response = requests.get(audio_url, stream=True)
            audio_temp = NamedTemporaryFile(delete=True)
            shutil.copyfileobj(response.raw, audio_temp)
            default_storage.save(filename, audio_temp)

        return url

    def _get_word_info(self, tree, word: str) -> Optional[DictionaryEntry]:
        """
        Returns the word information
        """
        audio = []  # type: List[str]
        audio = self._get_audio(tree)
        transcription = self._get_transcription(tree)

        entry = DictionaryEntry(
            pronunciation=self._save_audio(audio, word),
            transcription=transcription,
        )

        entry = self._get_examples(tree, entry)
        entry = self._get_definition(tree, entry)
        entry.process_data()

        return entry if entry.definition else None

    def _get_phrasal_verb_info(self, tree,
                               word: str) -> Optional[DictionaryEntry]:
        """
        Returns the phrasal verb word information
        """
        root = tree.find(".//dre[.='{}']/..".format(word))
        examples = definition = None
        if root:
            definition = self._get_phrasal_verb_definition(root)
            examples = self._get_phrasal_verb_examples(root)

        return DictionaryEntry(definition, examples) if definition else None

    @save_result('webster/{}.xml')
    def _make_request(self, word: str) -> Optional[str]:
        """
        Make a request to the API
        """
        url = f'{self.url}{word}?key={self.key}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None

    def get_result(self, **kwargs) -> Optional[DictionaryEntry]:
        """
        Returns the word or phrase entry
        """
        word = str(kwargs.get('word'))
        xml_text = self._make_request(word)
        if xml_text:
            try:
                tree = ElementTree.fromstring(xml_text)
            except ElementTree.ParseError:
                return None
            category = guess_category(word)
            if category != 'word':
                return self._get_phrasal_verb_info(tree, word)
            return self._get_word_info(tree, word)

        return None
