from typing import Dict

import arrow
from django.apps import apps

import cards
import nativecards.lib.settings as config
from nativecards.managers import LookupMixin


class CardManager(LookupMixin):
    """"
    The card objects manager
    """
    lookup_search_fields = ('=pk', 'word', 'definition', 'translation',
                            'examples', 'created_by__username',
                            'created_by__email', 'created_by__last_name')

    def get_lesson_new_cards(self, is_latest: bool, user,
                             deck_id: int = None) -> list:
        """
        Get the new cards for a lesson
        """
        query = self.filter(
            created_by=user, complete__lt=100).select_related(
                'created_by', 'modified_by', 'deck').order_by('?')
        if deck_id:
            query = query.filter(deck_id=deck_id)
        if is_latest:
            date = arrow.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0).shift(
                    days=-config.get('lesson_latest_days', user)).datetime
            query = query.filter(created__gte=date)

        return query[:config.get('cards_per_lesson', user)]

    def get_lesson_learned_cards(self, user) -> list:
        """
        Get the learned cards for a lesson
        """
        query = self.filter(
            created_by=user, complete=100).select_related(
                'created_by', 'modified_by', 'deck').order_by('?')
        return query[:config.get('cards_to_repeat', user)]


class AttemptManager(LookupMixin):
    """"
    The attempt objects manager
    """
    lookup_search_fields = ('=pk', 'card__word', 'answer',
                            'created_by__username', 'created_by__email',
                            'created_by__last_name')

    def get_statistics(self, user) -> Dict[str, int]:
        """
        Get the statistics of a studying process
        """
        cards_query = apps.get_model('cards.Card').objects.filter(
            created_by=user)
        query = self.filter(created_by=user)

        today = arrow.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0)

        week = today.shift(days=-7).datetime
        month = today.shift(months=-1).datetime
        today = today.datetime

        today_query = query.filter(created__gte=today)
        week_query = query.filter(created__gte=week)
        month_query = query.filter(created__gte=month)

        return {
            'today_attempts':
            today_query.count(),
            'today_correct_attempts':
            today_query.filter(is_correct=True).count(),
            'today_incorrect_attempts':
            today_query.filter(is_correct=False).count(),
            'week_attempts':
            week_query.count(),
            'week_correct_attempts':
            week_query.filter(is_correct=True).count(),
            'week_incorrect_attempts':
            week_query.filter(is_correct=False).count(),
            'month_attempts':
            month_query.count(),
            'month_correct_attempts':
            month_query.filter(is_correct=True).count(),
            'month_incorrect_attempts':
            month_query.filter(is_correct=False).count(),
            'total_cards':
            cards_query.count(),
            'learned_cards':
            cards_query.filter(complete=100).count(),
            'unlearned_cards':
            cards_query.filter(complete__lt=100).count(),
        }


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
            return self.filter(created_by=user).first()
