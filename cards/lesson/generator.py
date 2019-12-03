"""
Lesson module
"""

from copy import deepcopy
from random import choice, shuffle
from typing import List

from django.conf import settings
from django.http import HttpRequest

from cards.models import Attempt, Card


class LessonGenerator():
    """
    Class for generating the list of card for the user lesson
    """

    ORDERING = [
        'complete',
        'priority',
        'created',
    ]

    def __init__(self, request: HttpRequest) -> None:
        self.request = request
        self.user = self.request.user
        self.manager = Card.objects
        self._set_filter_params_from_query()
        self.attempt_forms = self._get_attempt_forms()

    def _set_filter_params_from_query(self):
        self.is_latest = bool(int(self.request.GET.get('is_latest', 0)))
        self.speak = bool(int(self.request.GET.get('speak', 0)))
        self.complete_gte = self.request.GET.get('complete__gte')
        self.complete_lte = self.request.GET.get('complete__lte')
        ordering = self.request.GET.get('ordering')
        self.ORDERING.extend(['-' + v for v in self.ORDERING])
        self.ordering = ordering if ordering in self.ORDERING else None
        self.deck_id = self.request.GET.get('deck')
        self.category = self.request.GET.get('category')

    def _get_attempt_forms(self):
        """
        Get attempt forms for the lesson (listen, write, speak)
        """
        forms = [f[0] for f in Attempt.FORMS]
        if not self.speak:
            forms.remove('speak')
        return forms

    def _get_cards(self) -> List[Card]:
        """
        Get cards objects for the lesson
        """
        new_cards = list(
            self.manager.get_lesson_new_cards(
                is_latest=self.is_latest,
                user=self.user,
                deck_id=self.deck_id,
                category=self.category,
                complete_lte=self.complete_lte,
                complete_gte=self.complete_gte,
                ordering=self.ordering,
            ))
        old_cards = list(self.manager.get_lesson_learned_cards(self.user))
        cards = new_cards * settings.NC_CARDS_REPEAT_IN_LESSON
        cards += old_cards

        return cards

    def _get_cards_with_choices_and_attempt_form(self, cards: List[Card]
                                                 ) -> List[Card]:
        random_words = self.manager.get_random_words(self.user)

        result = []
        for card in cards:
            card.form = choice(self.attempt_forms)
            card.choices = self.manager.select_random_words(
                words=random_words,
                additional=card.word,
            )
            result.append(deepcopy(card))
        shuffle(result)

        return result

    def get_lesson_cards(self) -> List[Card]:
        """
        Generate and return cards data for the lesson
        """
        cards = self._get_cards()
        return self._get_cards_with_choices_and_attempt_form(cards)
