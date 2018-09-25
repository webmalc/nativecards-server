from django.core.cache import cache
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import CachedModel


def _clear_cache(instance):
    if isinstance(instance, CachedModel):
        cache.clear()


@receiver(post_save, dispatch_uid='cached_model_post_save')
def cached_model_post_save(sender, **kwargs):
    """
    Cached model post save
    """
    _clear_cache(kwargs['instance'])


@receiver(pre_delete, dispatch_uid='cached_model_pre_delete')
def cached_model_pre_delete(sender, **kwargs):
    """
    Cached model pre delete
    """
    _clear_cache(kwargs['instance'])
