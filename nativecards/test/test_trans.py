"""
The tests module for the trans module
"""
import pytest
import requests
from django.core.cache import cache

from nativecards.lib.trans import GoogleTrans, Lingualeo, translate
from words.models import Word

pytestmark = pytest.mark.django_db  # pylint: disable=invalid-name


def test_translators_supported_languages():
    """
    Translators should only support selected languages
    """
    lingualeo = Lingualeo()
    google = GoogleTrans()

    assert lingualeo.check_language('ru')
    assert not lingualeo.check_language('es')
    assert google.check_language('ru')
    assert google.check_language('es')

    Lingualeo.supported_languages = ['xx']
    GoogleTrans.supported_languages = ['xx']

    assert not translate('god', 'ru')

    Lingualeo.supported_languages = ['ru']
    GoogleTrans.supported_languages = None


def test_google_translate():
    """
    Should return a word translation
    """
    google = GoogleTrans()
    translations = google.translate('cat', 'es')
    assert translations == ['gato']


def test_lingualeo_translate(mocker):
    """
    Should return a word translation
    """
    response = requests.Response()
    response.status_code = 200
    response.json = mocker.MagicMock(
        return_value={'translate': [{
            'value': 'test'
        }, {
            'value': 'кошка'
        }]})
    requests.get = mocker.MagicMock(return_value=response)
    lingualeo = Lingualeo()
    translations = lingualeo.translate('cat', 'ru')
    assert 'кошка' in translations


def test_translate(mocker):
    """
    Should return a word translation
    """
    cache.clear()
    response = requests.Response()
    response.status_code = 200
    response.json = mocker.MagicMock(
        return_value={'translate': [{
            'value': 'test'
        }, {
            'value': 'trans'
        }]})
    requests.get = mocker.MagicMock(return_value=response)
    result = translate('word', 'ru')
    word = Word.objects.get(word='word')
    translations = word.translations.copy()
    word.translations['ru'] = 'word trans'
    word.save()
    cache.clear()
    result_word = translate('word', 'ru')
    Lingualeo.supported_languages.append('es')
    word = translate('word', 'es')
    word_updated = Word.objects.get(word='word')

    assert 'trans' in result['translation']
    assert translations == {'ru': 'test, trans'}
    assert result_word['translation'] == 'word trans'
    assert word_updated.translations == {
        'ru': 'word trans',
        'es': 'test, trans',
    }


def test_lingualeo_errors(mocker):
    """
    Should return an empty list when an error occurred
    """
    lingualeo = Lingualeo()

    response = requests.Response()
    response.status_code = 404
    requests.get = mocker.MagicMock(return_value=response)
    translations = lingualeo.translate('cat', 'ru')
    assert len(translations) == 0

    response = requests.Response()
    response.status_code = 200
    response.json = mocker.MagicMock(return_value={'error_msg': 'error'})
    requests.get = mocker.MagicMock(return_value=response)

    translations = lingualeo.translate('cat', 'ru')
    assert len(translations) == 0
