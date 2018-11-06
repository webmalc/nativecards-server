from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from cards.models import Deck


@receiver(post_save, sender=User, dispatch_uid='user_post_save')
def user_post_save(instance, **kwargs):
    """
    User post save
    """

    # Create default deck
    if not Deck.objects.get_default(instance):
        deck = Deck()
        deck.created_by = instance
        deck.title = 'main'
        deck.is_default = True
        deck.save()
