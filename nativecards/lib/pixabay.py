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
    querystring = {"q": word}

    url = 'https://contextualwebsearch-websearch-v1.p.rapidapi.com/'
    url += 'api/Search/ImageSearchAPI'

    headers = {
        'X-RapidAPI-Host': 'contextualwebsearch-websearch-v1.p.rapidapi.com',
        'X-RapidAPI-Key': settings.NC_RAPIDAPI_KEY
    }
    response = requests.request(
        "GET",
        url,
        headers=headers,
        params=querystring,
    )
    if response.status_code == 200:
        result = []
        data = response.json()
        for v in data.get("value", list()):
            result.append({"previewURL": v["thumbnail"]})
        return result[:MAX_IMAGES]
    return []
