"""
The dictionary module
"""
from typing import Optional

import requests
from bs4 import BeautifulSoup

from nativecards.lib.dictionary import guess_category
from nativecards.lib.dicts.base import Dictionary, DictionaryEntry


class FreeDictionary(Dictionary):
    """
    The Free Dictionary
    """
    url: str = 'https://idioms.thefreedictionary.com/'

    @staticmethod
    def _get_definition_and_examples(soup: BeautifulSoup
                                     ) -> Optional[DictionaryEntry]:
        definitions = examples = ''
        entry_tags = soup.select('#Definition > section > .ds-single')
        for entry in entry_tags:
            definition = entry.text
            example_tags = entry.select('.illustration')
            for tag in example_tags:
                example = tag.text.strip()
                definition = definition.replace(example, '').strip()
                if example:
                    examples += '{}\n\n'.format(example)

            if definition:
                definitions += '{}\n\n'.format(definition)

        if definitions or examples:
            return DictionaryEntry(definitions, examples)
        return None

    def get_entry(self, word: str) -> Optional[DictionaryEntry]:
        """
        Returns the idiom entry
        """
        if guess_category(word) == 'word':
            return None
        url = '{}{}'.format(self.url, word.replace(' ', '+'))
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._get_definition_and_examples(soup)
        return None
