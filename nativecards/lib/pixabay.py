"""
Module for getting images
"""
import requests
from django.conf import settings

from nativecards.lib.cache import cache_result


@cache_result('images')
def get_images(word):
    """
    Get images from the pixabay.com
    """
    if not word:
        return {'error': 'The word parameter not found.'}

    url = 'https://pixabay.com/api/?key={}&q={}&min_width={}&\
orientation=horizontal'.format(settings.NC_PIXABAY_KEY, word.lower(),
                               settings.NC_IMAGE_WIDTH)
    result = requests.get(url)

    if result.status_code == 200:
        return result.json()['hits'][:5]
    return {'error': 'The service is unavailable.'}
