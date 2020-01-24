"""
The tests module for the dictionary module
"""
import os

import pytest
import requests
from django.conf import settings as global_settings
from django.core.cache import cache
from gtts import gTTS

from nativecards.lib.audio import check_audio_path
from nativecards.lib.dictionary import get_definition
from nativecards.lib.dicts.webster_learners import WebsterLearners
from nativecards.lib.dicts.words_api import WordsApi
from words.models import Word

pytestmark = pytest.mark.django_db  # pylint: disable=invalid-name


def test_webster_save_audio():
    """
    Should save an audio to the server
    """
    # pylint: disable-all
    url = WebsterLearners._save_audio(
        ['https://media.merriam-webster.com/soundc11/d/dog00002.wav'],
        'test webster word',
    )
    url_none = WebsterLearners._save_audio([], 'none word')
    filename = 'audio/test_webster_word.wav'

    assert url == 'http://localhost:8000/media/audio/test_webster_word.wav'
    assert check_audio_path(filename)
    assert url_none is None

    os.remove(os.path.join(global_settings.MEDIA_ROOT, filename))


def test_get_definition_errors_freedict(mocker):
    """
    Should return None when an error occurred
    """
    gTTS.save = mocker.MagicMock(return_value='some value')
    result = get_definition('')
    assert result['error'] == 'The word parameter not found.'

    response = requests.Response()
    response.status_code = 404
    requests.get = mocker.MagicMock(return_value=response)
    result = get_definition('to put it mildly')

    assert result is None

    response = requests.Response()
    response.status_code = 200
    content = '<html><body>test</body></html>'
    response._content = content.encode()  # pylint: disable=protected-access
    requests.get = mocker.MagicMock(return_value=response)
    result = get_definition('beat around the bush')

    assert result is None


def test_get_word_definition_wordsapi(mocker, settings):
    """
    Should return a dictionary with the definition
    and other information about the word
    """
    settings.NC_DICTIONARIES = ['nativecards.lib.dicts.words_api.WordsApi']
    cache.clear()
    gTTS.save = mocker.MagicMock(return_value='some value')
    response = requests.Response()
    response.status_code = 200

    path = os.path.join(global_settings.FIXTURE_DIRS[0],
                        'test/wordsapi/love.json')
    with open(path, 'r') as page:
        return_value = page.read()
    response._content = return_value.encode('utf-8')
    requests.get = mocker.MagicMock(return_value=response)
    result = get_definition('love')

    assert '[noun] any object of warm' in result['definition']
    assert '[verb] get pleasure from' in result['definition']
    assert '[noun] he has a very complicated' in result['examples']
    assert '[verb] I love cooking' in result['examples']
    assert '[noun] love life' in result['synonyms']
    assert '[verb] enjoy' in result['synonyms']
    assert '[verb] hate' in result['antonyms']
    assert 'lÉ™v' in result['transcription']


def test_get_definition_errors_wordsapi(mocker):
    """
    Should return None when an error occurred
    """
    response = requests.Response()
    response.status_code = 200
    response._content = '{"test": []}'.encode('utf-8')
    requests.get = mocker.MagicMock(return_value=response)

    words_api = WordsApi()
    result = words_api.get_result(word='wordsapi test word')

    assert result is None


def test_get_word_definition_freedict(mocker):
    """
    Should return a dictionary with the definition
    and other information about the word
    """
    gTTS.save = mocker.MagicMock(return_value='some value')
    path = os.path.join(global_settings.FIXTURE_DIRS[0],
                        'test/freedict/horse.html')
    with open(path, 'r') as page:
        page = page.read()
    response = requests.Response()
    response.status_code = 200
    response._content = page.encode()  # pylint: disable=protected-access
    requests.get = mocker.MagicMock(return_value=response)
    result = get_definition("get straight from the horse's mouth")
    audio = '/media/audio/get_straight_from_the_horses_mouth.mp3'

    assert 'obtain information from the original' in result['definition']
    assert 'to get information from the person most' in result['definition']
    assert 'section with a .ds-list container' in result['definition']
    assert 'section without a container' in result['definition']
    assert 'See also' not in result['definition']
    assert 'Yep, Mrs. Whitford told me' in result['examples']
    assert 'it until I get it straight from the horse' in result['examples']
    assert audio in result['pronunciation']


def test_get_phrasal_word_definition_webster(mocker):
    """
    Should return a dictionary with the definition
    and other information about the phrasal word
    """
    gTTS.save = mocker.MagicMock(return_value='some value')
    path = os.path.join(global_settings.FIXTURE_DIRS[0],
                        'test/webster/come_definition.xml')
    with open(path, 'r') as xml:
        xml = xml.read().replace('\n', '')
    response = requests.Response()
    response.status_code = 200
    response._content = xml.encode()  # pylint: disable=protected-access
    requests.get = mocker.MagicMock(return_value=response)
    result = get_definition('come up with')
    audio = 'http://localhost:8000/media/audio/come_up_with.mp3'

    assert 'to get or think of' in result['definition']
    assert 'We finally *came up with* a' in result['examples']
    assert result['pronunciation'] == audio
    assert result['transcription'] is None

    result = get_definition('come across')
    assert 'to seem to have a particular quality' in result['definition']


def test_get_word_definition_webster(mocker):
    """
    Should return a dictionary with the definition
    and other information about the word
    """
    # pylint: disable=W
    WebsterLearners._save_audio = mocker.MagicMock(return_value='cat.wav')
    gTTS.save = mocker.MagicMock(return_value='some value')
    path = os.path.join(global_settings.FIXTURE_DIRS[0],
                        'test/webster/cat_definition.xml')
    with open(path, 'r') as xml:
        xml = xml.read().replace('\n', '')
    response = requests.Response()
    response.status_code = 200
    response._content = xml.encode()
    requests.get = mocker.MagicMock(return_value=response)
    result = get_definition('cat')

    word = Word.objects.get(word='cat')
    word_values = word.__dict__.copy()
    word.definition = 'new test definition'
    word.examples = 'new test examples'
    word.save()
    cache.clear()
    result_word = get_definition('cat')

    assert 'cat.wav' in result['pronunciation']
    assert '[noun] I have two dogs and a *cat*' in result['examples']
    assert '[noun] a small animal that is related' in result['definition']
    assert '[verb] a thief who enter' in result['definition']
    assert 'test content' in result['definition']

    del result['data']
    assert result.items() <= word_values.items()
    assert result['transcription'] == 'ˈkæt'
    assert result_word['definition'] == 'new test definition'
    assert result_word['examples'] == 'new test examples'


def test_get_definition_errors_webster(mocker):
    """
    Should return None when an error occurred
    """
    gTTS.save = mocker.MagicMock(return_value='some value')
    result = get_definition('')
    assert result['error'] == 'The word parameter not found.'

    response = requests.Response()
    response.status_code = 404
    requests.get = mocker.MagicMock(return_value=response)
    result = get_definition('car')

    assert result is None

    response = requests.Response()
    response.status_code = 200
    response._content = 'invalid'.encode()  # pylint: disable=protected-access
    requests.get = mocker.MagicMock(return_value=response)
    result = get_definition('card')

    assert result is None

    response = requests.Response()
    response.status_code = 200
    content = '<?xml version="1.0" encoding="utf-8"?><entry_list></entry_list>'
    response._content = content.encode()  # pylint: disable=protected-access
    requests.get = mocker.MagicMock(return_value=response)
    result = get_definition('man')

    assert result is None
