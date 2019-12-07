"""
The tests module for the dictionary module
"""
import os

import requests
from django.conf import settings
from gtts import gTTS

from nativecards.lib.dictionary import get_defenition, get_synonyms


def test_get_phrasal_word_definition(mocker):
    """
    Should return a dictionary with the definition
    and other information about the phrasal word
    """
    gTTS.save = mocker.MagicMock(return_value='some value')
    path = os.path.join(settings.FIXTURE_DIRS[0],
                        'test/webster/come_definition.xml')
    with open(path, 'r') as xml:
        xml = xml.read().replace('\n', '')
    response = requests.Response()
    response.status_code = 200
    response._content = xml.encode()  # pylint: disable=protected-access
    requests.get = mocker.MagicMock(return_value=response)
    result = get_defenition('come up with')
    audio = 'http://localhost:8000/media/audio/come_up_with.mp3'

    assert 'to get or think of' in result['definition']
    assert 'We finally *came up with* a' in result['examples']
    assert result['pronunciation'] == audio
    assert result['transcription'] is None


def test_get_word_definition(mocker):
    """
    Should return a dictionary with the definition
    and other information about the word
    """
    gTTS.save = mocker.MagicMock(return_value='some value')
    path = os.path.join(settings.FIXTURE_DIRS[0],
                        'test/webster/cat_definition.xml')
    with open(path, 'r') as xml:
        xml = xml.read().replace('\n', '')
    response = requests.Response()
    response.status_code = 200
    response._content = xml.encode()  # pylint: disable=protected-access
    requests.get = mocker.MagicMock(return_value=response)
    result = get_defenition('cat')

    assert 'cat00001.wav' in result['pronunciation']
    assert 'I have two dogs and a *cat*' in result['examples']
    assert 'a small animal that is related to lions' in result['definition']
    assert 'test content' in result['definition']
    assert result['transcription'] == 'ˈkæt'


def test_get_definition_errors(mocker):
    """
    Should return None when an error occurred
    """
    gTTS.save = mocker.MagicMock(return_value='some value')
    result = get_defenition('')
    assert result['error'] == 'The word parameter not found.'

    response = requests.Response()
    response.status_code = 404
    requests.get = mocker.MagicMock(return_value=response)
    result = get_defenition('car')

    assert result is None

    response = requests.Response()
    response.status_code = 200
    response._content = 'invalid'.encode()  # pylint: disable=protected-access
    requests.get = mocker.MagicMock(return_value=response)
    result = get_defenition('card')

    assert result is None

    response = requests.Response()
    response.status_code = 200
    content = '<?xml version="1.0" encoding="utf-8"?><entry_list></entry_list>'
    response._content = content.encode()  # pylint: disable=protected-access
    requests.get = mocker.MagicMock(return_value=response)
    result = get_defenition('man')

    assert result['definition'] is None
    assert result['examples'] is None
    assert result['transcription'] is None


def test_get_synonyms(mocker):
    """
    Should return a dictionary with the synonyms and antonyms for the word
    """
    response = requests.Response()
    response.status_code = 200
    return_value = {
        "noun": {
            "syn": ["passion"],
            "ant": ["hate"],
            "usr": ["amour"]
        },
        "verb": {
            "syn": [
                "love",
                "enjoy",
            ],
            "ant": ["hate"]
        }
    }
    response.json = mocker.MagicMock(return_value=return_value)
    requests.get = mocker.MagicMock(return_value=response)
    result = get_synonyms('love')

    assert 'passion' in result['synonyms']
    assert 'enjoy' in result['synonyms']
    assert 'hate' in result['antonyms']


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

    assert not result['synonyms']
    assert not result['antonyms']
