import json

import pytest
from django.conf import settings
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_settings_get_by_user(client):
    response = client.get(reverse('settings-get'))
    assert response.status_code == 401


def test_settings_get_by_admin(admin_client):
    response = admin_client.get(reverse('settings-get'))
    data = response.json()

    assert response.status_code == 200
    assert data['cards_to_repeat'] == settings.NC_CARDS_TO_REPEAT
    assert data['attempts_to_remember'] == settings.NC_ATTEMPTS_TO_REMEMBER
    assert data['attempts_per_day'] == 65


def test_settings_update_by_admin(admin_client):
    data = json.dumps({'cards_to_repeat': 22, 'attempts_to_remember': 5})
    response = admin_client.patch(
        reverse('settings-save'), data=data, content_type="application/json")
    assert response.status_code == 200
    response = admin_client.get(reverse('settings-get'))
    data = response.json()
    assert data['cards_to_repeat'] == 22
    assert data['attempts_to_remember'] == 5
    assert data['cards_per_lesson'] == settings.NC_CARDS_PER_LESSON
