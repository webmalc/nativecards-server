from time import time

import pytest
from django.core.cache import cache

from nativecards.lib.cache import cache_result

pytestmark = pytest.mark.django_db


def test_cache_result_decorator():
    @cache_result('test_function')
    def test_function(arg):
        return time()

    result = test_function('test')

    assert test_function('test') == result
    assert test_function('test_another') != result
    cache.clear()
    assert test_function('test') != result
