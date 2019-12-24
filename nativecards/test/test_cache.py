"""
The cache test module
"""
from time import time

import pytest
from django.core.cache import cache
from django.core.files.storage import default_storage

from nativecards.lib.cache import cache_result, save_result

pytestmark = pytest.mark.django_db  # pylint: disable=invalid-name


def test_save_result_decorator(settings):
    """
    Should save a function results to the disk
    """
    settings.TESTS = False

    @save_result('tests/{}.txt')
    def test_function(arg, word):
        return '{}{}{}'.format(arg, word, time())

    result = test_function(None, 'test')

    assert default_storage.exists('tests/test.txt')
    assert test_function(None, 'test') == result
    assert test_function(None, 'test_another') != result

    default_storage.delete('tests/test.txt')
    assert test_function(None, 'test') != result

    default_storage.delete('tests/test.txt')
    default_storage.delete('tests/test_another.txt')


def test_cache_result_decorator():
    """
    Should save a function results to the cache storage
    """
    @cache_result('test_function')
    def test_function(arg):
        return '{}{}'.format(arg, time())

    result = test_function('test')

    assert test_function('test') == result
    assert test_function('test_another') != result
    cache.clear()
    assert test_function('test') != result
