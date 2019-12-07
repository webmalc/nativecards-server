"""
The tests module for the dictionary module
"""
import pytest
from gtts import gTTS

from nativecards.lib.audio import get_audio


def test_get_word_definition(mocker):
    """
    Should return create a file with the word pronunciation
    """
    gTTS.save = mocker.MagicMock(return_value='some value')
    url = get_audio('test test word')

    assert url == 'http://localhost:8000/media/audio/test_test_word.mp3'


def test_get_definition_errors():
    """
    Should raise an exception on an error
    """
    with pytest.raises(AttributeError) as error:
        get_audio('')
        assert error == 'The word parameter not found.'
