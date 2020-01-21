"""
The pytest fixtures module
"""
import pytest
from django.contrib.auth.models import User
from django.core.management import call_command

collect_ignore_glob = ["*/migrations/*"]  # pylint: disable=invalid-name


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    # pylint: disable=redefined-outer-name, unused-argument
    """
    Loads fixtures
    """
    with django_db_blocker.unblock():
        call_command(
            'loaddata',
            'test/users',
            'test/decks',
            'test/cards',
            'test/attempts',
        )


@pytest.fixture
def admin():
    """
    Return an admin user
    """
    return User.objects.get(pk=1)


@pytest.fixture
def user():
    """
    Return a common user
    """
    return User.objects.get(pk=2)
