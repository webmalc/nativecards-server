"""
The attempts test module
"""
import json

import pytest
from django.urls import reverse

from cards.models import Attempt, Card

pytestmark = pytest.mark.django_db  # pylint: disable=invalid-name


def test_attempt_score_calcultaion():
    """
    Scores should be calculated while saving attempt objects
    """
    attempt_correct = Attempt.objects.create(form='listen',
                                             card_id=1,
                                             is_correct=True)
    attempt_correct_hint = Attempt.objects.create(form='listen',
                                                  card_id=1,
                                                  is_correct=True,
                                                  is_hint=True)
    attempt_correct_hint_two = Attempt.objects.create(form='listen',
                                                      card_id=1,
                                                      is_correct=True,
                                                      is_hint=True,
                                                      hints_count=2)
    attempt_incorrect = Attempt.objects.create(form='listen',
                                               card_id=1,
                                               is_correct=False)
    attempt_incorrect_hint = Attempt.objects.create(form='listen',
                                                    card_id=1,
                                                    is_correct=False,
                                                    is_hint=True)

    attempt_incorrect_hint_two = Attempt.objects.create(form='listen',
                                                        card_id=1,
                                                        is_correct=False,
                                                        is_hint=True,
                                                        hints_count=2)
    assert attempt_correct.score == 10
    assert attempt_correct_hint.score == 5
    assert attempt_correct_hint_two.score == 3
    assert attempt_incorrect.score == 10
    assert attempt_incorrect_hint.score == 20
    assert attempt_incorrect_hint_two.score == 30
    assert Card.objects.get(pk=1).complete == 50 + 10 + 5 + 3 - 10 - 20 - 30


def test_attempts_list_by_user(client):
    """
    Should return 401 error code for non authenticated users
    """
    response = client.get(reverse('attempts-list'))
    assert response.status_code == 401


def test_attempts_list_by_admin(admin_client):
    """
    Should return the attempts list
    """
    response = admin_client.get(reverse('attempts-list'))
    data = response.json()['results']
    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]['answer'] == 'incorrect word one'


def test_attempts_create_by_admin(admin_client):
    """
    Should create an attempt object
    """
    data = json.dumps({
        'card': 1,
        'form': 'write',
        'is_correct': True,
        'answer': 'word one'
    })
    response = admin_client.post(reverse('attempts-list'),
                                 data=data,
                                 content_type="application/json")
    data = response.json()

    assert data['card'] == 1
    assert data['created_by'] == 'admin'
    assert data['score'] == 10

    response = admin_client.get(reverse('attempts-list'))
    assert len(response.json()['results']) == 3


def test_attempts_statistics_user(client):
    """
    Should return 401 error code for non authenticated users
    """
    response = client.get(reverse('attempts-statistics'))
    assert response.status_code == 401


def test_attempts_statistics_admin(admin_client, admin):
    """
    Should return the user statistics
    """
    Attempt.objects.create(form='listen',
                           card_id=1,
                           is_correct=False,
                           created_by=admin)
    for _ in range(0, 7):
        Attempt.objects.create(form='listen',
                               card_id=1,
                               is_correct=True,
                               created_by=admin)

    response = admin_client.get(reverse('attempts-statistics'))

    assert response.status_code == 200

    data = response.json()

    assert data == {
        'learned_cards': 1,
        'month_attempts': 8,
        'month_correct_attempts': 7,
        'month_incorrect_attempts': 1,
        'today_attempts': 8,
        'today_attempts_remain': 62,
        'today_attempts_to_complete': 70,
        'today_correct_attempts': 7,
        'today_incorrect_attempts': 1,
        'total_cards': 2,
        'unlearned_cards': 1,
        'week_attempts': 8,
        'week_correct_attempts': 7,
        'week_incorrect_attempts': 1
    }
