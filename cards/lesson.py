from collections import OrderedDict
from copy import deepcopy
from random import choice, shuffle
from typing import Any, List

from django.conf import settings
from django.http import HttpRequest

from .models import Attempt, Card


class LessonGenerator(object):
    """
    Class for generating the user lesson
    """

    def __init__(self, request: HttpRequest, serializer) -> None:
        self.request = request
        self.user = self.request.user
        self.serializer = serializer
        self.is_latest = bool(int(self.request.GET.get('is_latest', 0)))
        self.speak = bool(int(self.request.GET.get('speak', 0)))
        self.deck = self.request.GET.get('deck')
        self.category = self.request.GET.get('category')
        self.manager = Card.objects
        self.attempt_forms = self._get_attempt_forms()

    def _get_attempt_forms(self):
        """
        Get attempt forms for the lesson (listen, write, speak)
        """
        forms = [f[0] for f in Attempt.FORMS]
        if not self.speak:
            forms.remove('speak')
        return forms

    def _get_cards(self) -> List[OrderedDict]:
        """
        Get cards objects for the lesson
        """
        new_cards = self.manager.get_lesson_new_cards(
            self.is_latest,
            self.user,
            self.deck,
            self.category,
        )
        old_cards = self.manager.get_lesson_learned_cards(self.user)

        new_cards_data = self.serializer(new_cards, many=True).data
        old_cards_data = self.serializer(old_cards, many=True).data
        cards = new_cards_data * settings.NC_CARDS_REPEAT_IN_LESSON
        cards += old_cards_data

        return cards

    def _get_cards_with_choices_and_attempt_form(
            self, cards: List[OrderedDict]) -> List[OrderedDict]:
        random_words = self.manager.get_random_words(self.user)

        result = []
        for w in cards:
            w['form'] = choice(self.attempt_forms)
            w['choices'] = self.manager.select_random_words(
                words=random_words,
                additional=w['word'],
            )
            result.append(deepcopy(w))
        shuffle(result)

        return result

    def get_lesson_cards(self) -> List[Any]:
        """
        Generate and return cards data for the lesson
        """
        cards = self._get_cards()
        return self._get_cards_with_choices_and_attempt_form(cards)
