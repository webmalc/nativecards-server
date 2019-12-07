"""
The audio module
"""
import os
import re

from django.conf import settings
from gtts import gTTS

from nativecards.lib.cache import cache_result  # pylint: disable=import-error


@cache_result('pronunciation')
def get_audio(word: str) -> str:
    """
    Get the word's pronunciation
    """
    if not word:
        raise AttributeError('The word parameter not found.')

    filename = re.sub(r'[^A-Za-z\s]+', '', word).lower().replace(' ', '_')
    filename = 'audio/{}.mp3'.format(filename)
    fullpath = os.path.join(settings.MEDIA_ROOT, filename)
    url = os.path.join(settings.MEDIA_URL, filename)
    url = settings.NC_FILES_DOMAIN + url

    if not os.path.isfile(fullpath):
        tts = gTTS(word, lang='en')
        tts.save(fullpath)

    return url
