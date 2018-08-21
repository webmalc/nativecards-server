import json

import pytest
from django.urls import reverse

from cards.models import Card

pytestmark = pytest.mark.django_db


def test_cards_set_default_deck(admin):
    card = Card()
    card.word = 'word'
    card.created_by = admin
    card.save()

    assert card.deck.description == 'the main deck'


def test_cards_list_by_user(client):
    response = client.get(reverse('cards-list'))
    assert response.status_code == 401


def test_cards_list_by_admin(admin_client):
    response = admin_client.get(reverse('cards-list') + '?ordering=id')
    data = response.json()['results']
    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]['definition'] == 'word one definition'


def test_cards_display_by_user(client):
    response = client.get(reverse('cards-detail', args=[2]))
    assert response.status_code == 401


def test_cards_display_by_admin(admin_client):
    response = admin_client.get(reverse('cards-detail', args=[2]))
    assert response.status_code == 200
    assert response.json()['word'] == 'word two'


def test_cards_display_another_user_by_admin(admin_client):
    response = admin_client.get(reverse('cards-detail', args=[3]))
    assert response.status_code == 404


def test_cards_create_by_admin(admin_client):
    data = json.dumps({
        'word': 'new test word',
        'definition': 'test word definition',
        'remote_image': 'https://via.placeholder.com/550x400'
    })
    response = admin_client.post(
        reverse('cards-list'), data=data, content_type="application/json")
    data = response.json()

    assert data['word'] == 'new test word'
    assert data['created_by'] == 'admin'
    assert data['deck'] == 1
    assert '_4.png' in data['image']

    response = admin_client.get(reverse('cards-list'))
    assert len(response.json()['results']) == 3
