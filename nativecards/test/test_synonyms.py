"""
The tests module for the dictionary module
"""

import os

import pytest
import requests
from django.conf import settings as global_settings
from django.core.cache import cache

from nativecards.lib.synonyms import get_synonyms
from words.models import Word

pytestmark = pytest.mark.django_db  # pylint: disable=invalid-name


def test_get_synonyms_wordsapi(mocker, settings):
    """
    Should return a dictionary with the synonyms and antonyms for the word
    """
    # pylint: disable-all
    settings.NC_THESAURI = ['nativecards.lib.dicts.words_api.WordsApi']
    cache.clear()
    response = requests.Response()
    response.status_code = 200

    path = os.path.join(global_settings.FIXTURE_DIRS[0],
                        'test/wordsapi/love.json')
    with open(path, 'r') as page:
        return_value = page.read()

    response._content = return_value.encode('utf-8')
    requests.get = mocker.MagicMock(return_value=response)
    result = get_synonyms('love')

    assert '[noun] love' in result['synonyms']
    assert 'lovemaking' in result['synonyms']
    assert 'beloved' in result['synonyms']
    assert '[verb] enjoy' in result['synonyms']
    assert '[noun] hate' in result['antonyms']
    assert '[verb] hate' in result['antonyms']


def test_get_synonyms_bighuge(mocker, settings):
    """
    Should return a dictionary with the synonyms and antonyms for the word
    """

    settings.NC_THESAURI = ['nativecards.lib.synonyms.BigHugeThesaurus']
    cache.clear()
    response = requests.Response()
    response.status_code = 200
    return_value = {
        "noun": {
            "syn": ["bighuge passion"],
            "ant": ["bighuge hate"],
            "usr": ["bighuge amour"]
        },
        "verb": {
            "syn": [
                "bighuge love",
                "bighuge enjoy",
            ],
            "ant": ["hate"]
        }
    }
    response.json = mocker.MagicMock(return_value=return_value)
    requests.get = mocker.MagicMock(return_value=response)
    result = get_synonyms('love')
    word = Word.objects.get(word='love')
    word_synonyms = word.synonyms
    word_antonyms = word.antonyms
    word.synonyms = 'word_synonyms'
    word.save()
    cache.clear()
    word_result = get_synonyms('love')

    assert '[noun] bighuge passion' in result['synonyms']
    assert '[verb] bighuge love' in result['synonyms']
    assert 'bighuge enjoy' in result['synonyms']
    assert word_synonyms == result['synonyms']
    assert word_antonyms == result['antonyms']
    assert '[verb] hate' in result['antonyms']
    assert word_result['synonyms'] == 'word_synonyms'


def test_get_synonyms_errors(mocker):
    """
    Should return an empty dictionary when an error occurred
    """
    result = get_synonyms('')
    assert result['error'] == 'The word parameter not found.'

    response = requests.Response()
    response.status_code = 404
    requests.get = mocker.MagicMock(return_value=response)
    result = get_synonyms('car')

    assert not result
