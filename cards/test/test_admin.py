"""
The cards admin test module
"""
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db  # pylint: disable=invalid-name


def test_card_admin_audio(admin_client):
    """
    Should return an audio HTML tag
    """
    response = admin_client.get(reverse('admin:cards_card_changelist'))
    content = str(response.content)
    assert '<audio id="audio_1">' in content
    assert '<audio id="audio_2">' not in content


def test_card_admin_form(admin_client):
    """
    Test the card admin form
    """
    response = admin_client.get(reverse('admin:cards_card_change', args=[1]))
    content = str(response.content)
    assert '<option value="1" selected>main' in content
