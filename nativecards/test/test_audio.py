"""
The tests module for the dictionary module
"""
import os

import pytest
from django.conf import settings

from nativecards.lib.audio import get_audio


def test_get_word_definition():
    """
    Should return create a file with the word pronunciation
    """
    fullpath = os.path.join(settings.MEDIA_ROOT, 'audio/test_test_word.mp3')
    if os.path.isfile(fullpath):
        os.remove(fullpath)
    url = get_audio('test test word')

    assert url == 'http://localhost:8000/media/audio/test_test_word.mp3'
    assert os.path.isfile(fullpath)
    os.remove(fullpath)


def test_get_definition_errors():
    """
    Should raise an exception on an error
    """
    with pytest.raises(AttributeError) as error:
        get_audio('')
        assert error == 'The word parameter not found.'
