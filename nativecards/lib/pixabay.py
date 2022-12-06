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
    url = "https://bing-image-search1.p.rapidapi.com/images/search"
    headers = {
        'X-RapidAPI-Host': 'bing-image-search1.p.rapidapi.com',
        'X-RapidAPI-Key': settings.NC_RAPIDAPI_KEY
    }
    response = requests.request("GET",
                                url,
                                headers=headers,
                                params=querystring)
    if response.status_code == 200:
        result = []
        data = response.json()
        for v in data.get("value", list()):
            result.append({"previewURL": v["thumbnailUrl"]})
        return result[:MAX_IMAGES]
    return []
