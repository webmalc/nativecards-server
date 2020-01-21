"""
The FreeDictionary module
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
    def _get_definition_and_examples(
            soup: BeautifulSoup) -> Optional[DictionaryEntry]:
        definitions = examples = ''
        for section in soup.select('#Definition > section'):
            entry_tags = section.select('.ds-single')
            if not entry_tags:
                entry_tags = section.select('.ds-list')
            if not entry_tags:
                entry_tags = [section]
            see_also = section.select_one('.SeeAlso')
            see_also = see_also.text if see_also else ''
            for entry in entry_tags:
                definition = entry.text
                definition = definition.replace(see_also, '')
                example_tags = entry.select('.illustration')
                for tag in example_tags:
                    example = tag.text.strip()
                    definition = definition.replace(example, '').strip()
                    if example:
                        examples += f'{example}\n\n'

                if definition:
                    definitions += f'{definition}\n\n'

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
