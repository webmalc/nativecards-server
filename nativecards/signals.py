"""
The nativecards signals module
"""
from django.core.cache import cache
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from nativecards.lib.settings import clear_mermory_cache

from .models import CachedModel, Settings


def _clear_cache(instance):
    if isinstance(instance, CachedModel):
        cache.clear()


@receiver(post_save, sender=Settings, dispatch_uid='settings_post_save')
def settings_post_save(**kwargs):
    """
    Settings post save
    """
    clear_mermory_cache(kwargs['instance'].created_by)


@receiver(post_save, dispatch_uid='cached_model_post_save')
def cached_model_post_save(**kwargs):
    """
    Cached model post save
    """
    _clear_cache(kwargs['instance'])


@receiver(pre_delete, dispatch_uid='cached_model_pre_delete')
def cached_model_pre_delete(**kwargs):
    """
    Cached model pre delete
    """
    _clear_cache(kwargs['instance'])
