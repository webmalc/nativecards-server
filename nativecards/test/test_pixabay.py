"""
The tests module for the pixabay module
"""
import requests

from nativecards.lib.pixabay import get_images


def test_get_images(mocker):
    """
    Should return a word translation
    """
    response = requests.Response()
    response.status_code = 200
    response.json = mocker.MagicMock(
        return_value={'hits': [1, 2, 3, 4, 5, 6, 7]})
    requests.get = mocker.MagicMock(return_value=response)
    result = get_images('dog')
    assert len(result) == 5


def test_get_images_errors(mocker):
    """
    Should return an error when an error occurred
    """
    result = get_images('')
    assert result['error'] == 'The word parameter not found.'

    response = requests.Response()
    response.status_code = 404
    requests.get = mocker.MagicMock(return_value=response)
    result = get_images('cat')
    assert result['error'] == 'The service is unavailable.'
