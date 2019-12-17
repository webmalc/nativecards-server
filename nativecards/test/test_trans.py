"""
The tests module for the trans module
"""
import requests

from nativecards.lib.trans import GoogleTrans, Lingualeo, translate


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
