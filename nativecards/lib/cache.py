"""
The cache module
"""
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def save_result(path):
    """
    Save function result one the disk
    """
    def save_decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            filename = path.format(args[1])
            tests = settings.TESTS
            if not default_storage.exists(filename) or tests:
                result = func(*args, **kwargs)
                if not settings.TESTS:
                    json_file = ContentFile(str(result))
                    default_storage.save(filename, json_file)
            else:
                cached_file = default_storage.open(filename)
                result = cached_file.read().decode('utf-8')
                cached_file.close()
            return result

        return func_wrapper

    return save_decorator


def cache_result(key):
    """
    Save function result in the cache
    key - cache key
    """
    def cache_decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            key_with_args = '{}_{}_{}'.format(key, str(args), str(kwargs))
            key_with_args = key_with_args.replace(' ', '_')
            cached_result = cache.get(key_with_args)
            if cached_result is not None:
                return cached_result
            result = func(*args, **kwargs)
            cache.set(key_with_args, result)
            return result

        return func_wrapper

    return cache_decorator
