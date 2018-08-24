from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CachedModel


@receiver(post_save, dispatch_uid='cached_model_post_save')
def cached_model_post_save(sender, **kwargs):
    """
    Cached model post save
    """
    if isinstance(kwargs['instance'], CachedModel):
        cache.clear()
