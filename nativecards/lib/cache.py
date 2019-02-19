from functools import wraps

from django.core.cache import cache


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
