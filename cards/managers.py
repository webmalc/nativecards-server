import cards
from nativecards.managers import LookupMixin


class DeckManager(LookupMixin):
    """"
    The deck manager
    """
    lookup_search_fields = ('=pk', 'title', 'description',
                            'created_by__username', 'created_by__email',
                            'created_by__last_name')

    def filter_default(self, user, exclude_pk=None):
        """
        Filter default decks for user
        """
        query = self.filter(is_default=True, created_by=user)
        if exclude_pk:
            query = query.exclude(pk=exclude_pk)

        return query

    def get_default(self, user):
        """
        Get the default deck for user
        """
        query = self.filter_default(user)
        try:
            return query.get()
        except cards.models.Deck.DoesNotExist:
            return None
