import pytest
from django.contrib.auth.models import User
from django.core.management import call_command

collect_ignore_glob = ["*/migrations/*"]


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'test/users', 'test/decks', 'test/cards',
                     'test/attempts')


@pytest.fixture
def admin():
    return User.objects.get(pk=1)


@pytest.fixture
def user():
    return User.objects.get(pk=2)
