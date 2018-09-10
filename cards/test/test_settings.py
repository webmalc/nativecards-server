import json

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


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
