"""
The audio module
"""
import os
import re

from django.conf import settings
from gtts import gTTS

from nativecards.lib.cache import cache_result  # pylint: disable=import-error


def get_audio_filename(word: str, ext: str = 'mp3') -> str:
    """
    Get an audio file path
    """
    filename = re.sub(r'[^A-Za-z\s]+', '', word).lower().replace(' ', '_')
    filename = 'audio/{}.{}'.format(filename, ext)
    return filename


def get_audio_url(filename: str) -> str:
    """
    Get an audio file URL
    """
    url = os.path.join(settings.MEDIA_URL, filename)
    return settings.NC_FILES_DOMAIN + url


def check_audio_path(filename: str) -> bool:
    """
    Check if the file exists
    """
    fullpath = os.path.join(settings.MEDIA_ROOT, filename)
    return os.path.isfile(fullpath)


@cache_result('pronunciation')
def get_audio(word: str) -> str:
    """
    Get the word's pronunciation
    """
    if not word:
        raise AttributeError('The word parameter not found.')

    filename = get_audio_filename(word)
    url = get_audio_url(filename)

    if not check_audio_path(filename):
        tts = gTTS(word, lang='en')
        tts.save(os.path.join(settings.MEDIA_ROOT, filename))

    return url
