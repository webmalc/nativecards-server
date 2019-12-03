"""
The tests module for the trans module
"""
import requests

from nativecards.lib.trans import Lingualeo


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
    translations = lingualeo.translate('cat')
    assert 'кошка' in translations


def test_lingualeo_errors(mocker):
    """
    Should return an empty list when an error occurred
    """
    lingualeo = Lingualeo()

    response = requests.Response()
    response.status_code = 404
    requests.get = mocker.MagicMock(return_value=response)
    translations = lingualeo.translate('cat')
    assert len(translations) == 0

    response = requests.Response()
    response.status_code = 200
    response.json = mocker.MagicMock(return_value={'error_msg': 'error'})
    requests.get = mocker.MagicMock(return_value=response)

    translations = lingualeo.translate('cat')
    assert len(translations) == 0
