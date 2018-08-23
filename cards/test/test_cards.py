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


def test_cards_limit_complete_deck(admin):
    card = Card()
    card.word = 'word'
    card.complete = 122
    card.created_by = admin
    card.save()

    assert card.complete == 100

    card.complete = -23
    card.save()
    assert card.complete == 0


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


def test_cards_images_by_user(client):
    response = client.get(reverse('cards-images'))
    assert response.status_code == 401


def test_cards_images_by_admin(admin_client):
    response = admin_client.get(reverse('cards-images'))
    assert response.status_code == 200
    assert response.json()['error'] == 'The word parameter not found.'

    response = admin_client.get(reverse('cards-images') + '?word=dog')
    assert response.status_code == 200
    assert len(response.json()) == 5
    assert 'previewURL' in response.json()[0]


def test_cards_translation_by_user(client):
    response = client.get(reverse('cards-translation'))
    assert response.status_code == 401


def test_cards_translation_by_admin(admin_client):
    response = admin_client.get(reverse('cards-translation'))
    assert response.status_code == 200
    assert response.json()['error'] == 'The word parameter not found.'

    response = admin_client.get(reverse('cards-translation') + '?word=dog')
    assert response.status_code == 200
    assert 'собака' in response.json()['translation']


def test_cards_definition_by_user(client):
    response = client.get(reverse('cards-definition'))
    assert response.status_code == 401


def test_cards_definition_by_admin(admin_client):
    response = admin_client.get(reverse('cards-definition'))
    assert response.status_code == 200
    assert response.json()['error'] == 'The word parameter not found.'

    response = admin_client.get(reverse('cards-definition') + '?word=dog')
    assert response.status_code == 200
    assert '.wav' in response.json()['pronunciation']
    assert '<i>dog</i>' in response.json()['examples']
    assert 'animal' in response.json()['definition']


def test_cards_lesson_by_user(client):
    response = client.get(reverse('cards-lesson'))
    assert response.status_code == 401


def test_cards_lesson_by_admin(admin_client, admin, settings):
    settings.NC_LESSON_LATEST_DAYS = 1
    response = admin_client.get(reverse('cards-lesson') + '?deck=1')
    assert response.status_code == 200
    data_one = response.json()

    response = admin_client.get(reverse('cards-lesson') + '?deck=1')
    assert response.status_code == 200
    data_two = response.json()

    Card.objects.create(word='new word', created_by=admin)
    Card.objects.create(word='completed word', created_by=admin, complete=100)
    response = admin_client.get(reverse('cards-lesson') + '?is_latest=1')
    assert response.status_code == 200
    data_latest = response.json()
    words = [d['word'] for d in data_latest]
    words.sort()

    assert len(data_one) == 6
    assert len(data_two) == 6
    assert data_one != data_two
    assert len(data_latest) == 4
    assert set(words) == {'completed word', 'new word'}
