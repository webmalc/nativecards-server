"""
The nativecards admin test module
"""
import pytest
from django.urls import reverse

from nativecards.models import Settings

pytestmark = pytest.mark.django_db  # pylint: disable=invalid-name


def test_settings_admin_form(admin_client):
    """
    Test the settings admin form
    """
    admin_client.get(reverse('settings-get'))
    settings_id = Settings.objects.all().first().pk
    response = admin_client.get(
        reverse('admin:nativecards_settings_change', args=[settings_id]))
    assert response.status_code == 200

    response = admin_client.post(reverse('admin:nativecards_settings_add'))
    assert 'The settings object already exists for this user' in str(
        response.content)

    response = admin_client.post(
        reverse('admin:nativecards_settings_change', args=[settings_id]))
    assert response.status_code == 200
