"""
The cards managers module
"""
from random import sample, shuffle
from typing import Dict, Iterable, List

import arrow
from django.apps import apps
from django.db import models

import cards
import nativecards.lib.settings as config
from nativecards.models import Settings


class CardManager(models.Manager):
    """"
    The card objects manager
    """
    lookup_search_fields = ('=pk', 'word', 'definition', 'translation',
                            'examples', 'created_by__username',
                            'created_by__email', 'created_by__last_name')

    def get_random_words(self, user, limit: int = 100) -> Iterable[str]:
        """
        Get random words from the user dictionary
        """
        words = self.filter(created_by=user).values_list(
            'word', flat=True).order_by('?')[:limit]
        return words

    def select_random_words(self,
                            user=None,
                            words: Iterable[str] = None,
                            additional: str = None,
                            limit: int = 3) -> List[str]:
        """
        Select random words from the user dictionary
        """
        if not words and not user:
            raise ValueError(
                'the user and words fields are empty at the same time')
        if not words:
            words = self.get_random_words(user)
        words = list(words)
        if additional:
            limit += 1
        choices = sample(words, min([len(words), limit]))
        if additional and additional not in choices:
            del choices[0]
            choices.append(additional)
        shuffle(choices)

        return choices

    def get_lesson_new_cards(
            self,
            is_latest: bool,
            user,
            deck_id: int = None,
            category: str = None,
            complete_lte: int = 99,
            complete_gte: int = None,
            ordering: str = None,
    ) -> list:
        """
        Get the new cards for a lesson
        """
        complete_lte = complete_lte if complete_lte else 99
        query = self.filter(created_by=user,
                            complete__lte=complete_lte).select_related(
                                'created_by', 'modified_by',
                                'deck').order_by('?')
        if ordering:
            query = query.order_by(ordering)
        if complete_gte:
            query = query.filter(complete__gte=complete_gte)
        if deck_id:
            query = query.filter(deck_id=deck_id)
        if category:
            query = query.filter(category=category)
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
        query = self.filter(created_by=user, complete=100).select_related(
            'created_by', 'modified_by', 'deck').order_by('?')
        return query[:config.get('cards_to_repeat', user)]


class AttemptManager(models.Manager):
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
        settings = Settings.objects.get_by_user(user)

        today = arrow.utcnow().replace(hour=0,
                                       minute=0,
                                       second=0,
                                       microsecond=0)

        week = today.shift(days=-7).datetime
        month = today.shift(months=-1).datetime
        today = today.datetime

        today_query = query.filter(created__gte=today)
        today_attempts = today_query.count()
        week_query = query.filter(created__gte=week)
        month_query = query.filter(created__gte=month)
        to_complete = settings.attempts_per_day

        return {
            'today_attempts':
            today_attempts,
            'today_attempts_to_complete':
            to_complete,
            'today_attempts_remain':
            to_complete - today_attempts,
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


class DeckManager(models.Manager):
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
