import json

import pytest
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from cards.models import Deck

pytestmark = pytest.mark.django_db


class DeckTestCase(TestCase):
    def test_deck_api_cache(self):
        admin_client = self.client
        admin_client.login(username='admin', password='password')
        url = reverse('decks-list')

        with self.assertNumQueries(4):
            admin_client.get(url)
        with self.assertNumQueries(2):
            admin_client.get(url)


def test_deck_is_default_filter(admin, user):
    admin_decks = Deck.objects.filter_default(admin)
    admin_decks_exclude = Deck.objects.filter_default(admin, exclude_pk=1)
    user_decks = Deck.objects.filter_default(user)

    assert admin_decks.count() == 1
    assert admin_decks.first().title == 'main'
    assert admin_decks.first().is_default is True

    assert admin_decks_exclude.count() == 0

    assert user_decks.count() == 1
    assert user_decks.first().title == 'main test deck'
    assert admin_decks.first().is_default is True


def test_deck_is_default_get(admin, user):
    admin_deck = Deck.objects.get_default(admin)
    user_deck = Deck.objects.get_default(user)
    Deck.objects.filter(pk=1).delete()
    admin_deck_first = Deck.objects.get_default(admin)
    Deck.objects.all().delete()
    admin_deck_delete = Deck.objects.get_default(admin)

    assert admin_deck.title == 'main'
    assert admin_deck.is_default is True
    assert user_deck.title == 'main test deck'
    assert user_deck.is_default is True
    assert admin_deck_first.title == 'remember'
    assert admin_deck_delete is None


def test_deck_is_default_change(admin, user):
    old_main_deck = Deck.objects.get_default(admin)

    deck = Deck()
    deck.title = 'new main deck'
    deck.created_by = admin
    deck.is_default = True
    deck.save()

    new_main_deck = Deck.objects.get_default(admin)

    assert old_main_deck.title == 'main'
    assert old_main_deck.is_default is True

    old_main_deck.refresh_from_db()
    assert new_main_deck.is_default is True
    assert old_main_deck.is_default is False
    assert Deck.objects.get_default(user).title == 'main test deck'


def test_deck_get_remote_image(admin):
    deck = Deck.objects.get_default(admin)
    assert deck.image.width == 350

    deck.remote_image = 'https://via.placeholder.com/550x400'
    deck.save()
    deck.refresh_from_db()

    assert deck.image.width == 350

    deck.image = None
    deck.save()
    deck.refresh_from_db()

    assert deck.image.width is settings.NC_IMAGE_WIDTH
    assert '_1' in deck.image.url


def test_decks_list_by_user(client):
    response = client.get(reverse('decks-list'))
    assert response.status_code == 401


def test_decks_list_by_admin(admin_client):
    response = admin_client.get(reverse('decks-list') + '?ordering=id')
    data = response.json()['results']
    assert response.status_code == 200
    assert len(data) == 3
    assert data[0]['description'] == 'the main deck'


def test_decks_display_by_user(client):
    response = client.get(reverse('decks-detail', args=[2]))
    assert response.status_code == 401


def test_decks_display_by_admin(admin_client):
    response = admin_client.get(reverse('decks-detail', args=[3]))
    assert response.status_code == 200
    assert response.json()['title'] == 'animals'


def test_decks_display_another_user_by_admin(admin_client):
    response = admin_client.get(reverse('decks-detail', args=[4]))
    assert response.status_code == 404


def test_decks_create_by_admin(admin_client):
    data = json.dumps({
        'title': 'new test deck',
        'description': 'test description',
        'remote_image': 'https://via.placeholder.com/550x400'
    })
    response = admin_client.post(
        reverse('decks-list'), data=data, content_type="application/json")
    data = response.json()

    assert data['title'] == 'new test deck'
    assert data['created_by'] == 'admin'
    assert '_5.png' in data['image']

    response = admin_client.get(reverse('decks-list'))
    assert len(response.json()['results']) == 4
