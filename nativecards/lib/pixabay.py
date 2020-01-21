"""
Module for getting images
"""
import requests
from django.conf import settings

from nativecards.lib.cache import cache_result

MAX_IMAGES = 5


@cache_result('images')
def get_images(word):
    """
    Get images from the pixabay.com
    """
    if not word:
        return {'error': 'The word parameter not found.'}
    url = (f'https://pixabay.com/api/?key={settings.NC_PIXABAY_KEY}'
           f'&q={word.lower()}&min_width={settings.NC_IMAGE_WIDTH}&'
           'orientation=horizontal')
    result = requests.get(url)

    if result.status_code == 200:
        return result.json()['hits'][:MAX_IMAGES]
    return {'error': 'The service is unavailable.'}
