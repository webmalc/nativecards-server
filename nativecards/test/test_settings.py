"""
The tests module for the dictionary module
"""
import json

import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from nativecards.lib.dicts.free_dictionary import FreeDictionary
from nativecards.lib.dicts.webster_learners import WebsterLearners
from nativecards.lib.dicts.words_api import WordsApi
from nativecards.lib.settings import clear_mermory_cache, get, get_instances
from nativecards.models import Settings

pytestmark = pytest.mark.django_db  # pylint: disable=invalid-name


class CalcTestCase(TestCase):
    """
    The calculation test case
    """
    def test_calc_api_cache(self):
        """
        Should cache settings in memory
        """
        admin = User.objects.get(username='admin')
        clear_mermory_cache(admin)
        with self.assertNumQueries(2):
            assert get('attempts_to_remember', admin) == 10
        with self.assertNumQueries(0):
            assert get('attempts_to_remember', admin) == 10

        user_settings = Settings.objects.get_by_user(admin)
        user_settings.attempts_to_remember = 5
        user_settings.save()

        with self.assertNumQueries(1):
            assert get('attempts_to_remember', admin) == 5
        with self.assertNumQueries(0):
            assert get('attempts_to_remember', admin) == 5


def test_settings_get_instances():
    """
    Should return a generator with class instances from the settings
    """
    dicts = get_instances('DICTIONARIES')

    assert isinstance(next(dicts), WebsterLearners)
    assert isinstance(next(dicts), WordsApi)
    assert isinstance(next(dicts), FreeDictionary)


def test_settings_get_default():
    """
    Should return the default value if the user is not provided
    """
    assert get('attempts_to_remember') == 10


def test_settings_get_by_user(client):
    """
    Should return 401 error code for non authenticated users
    """
    response = client.get(reverse('settings-get'))
    assert response.status_code == 401


def test_settings_get_by_admin(admin_client):
    """
    Should display an user settings
    """
    response = admin_client.get(reverse('settings-get'))
    data = response.json()

    assert response.status_code == 200
    assert data['cards_to_repeat'] == settings.NC_CARDS_TO_REPEAT
    assert data['attempts_to_remember'] == settings.NC_ATTEMPTS_TO_REMEMBER
    assert data['attempts_per_day'] == 70


def test_settings_update_by_admin(admin_client):
    """
    Should update an user settings
    """
    data = json.dumps({'cards_to_repeat': 22, 'attempts_to_remember': 5})
    response = admin_client.patch(reverse('settings-save'),
                                  data=data,
                                  content_type="application/json")
    assert response.status_code == 200
    response = admin_client.get(reverse('settings-get'))
    data = response.json()
    assert data['cards_to_repeat'] == 22
    assert data['attempts_to_remember'] == 5
    assert data['cards_per_lesson'] == settings.NC_CARDS_PER_LESSON
