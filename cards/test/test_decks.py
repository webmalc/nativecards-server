import pytest
from django.conf import settings
from django.contrib.auth.models import User

from cards.models import Deck

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin():
    return User.objects.get(pk=1)


@pytest.fixture
def user():
    return User.objects.get(pk=2)


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
    assert admin_deck_first.title == 'remeber'
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
