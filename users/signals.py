"""
The users signals module
"""
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from cards.models import Deck


@receiver(post_save, sender=User, dispatch_uid='user_post_save')
def user_post_save(**kwargs):
    """
    User post save
    """
    Deck.objects.create_default(kwargs['instance'])
