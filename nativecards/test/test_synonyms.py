"""
The tests module for the dictionary module
"""

import requests

from nativecards.lib.synonyms import get_synonyms


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
