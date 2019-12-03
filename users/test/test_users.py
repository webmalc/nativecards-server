import json

import pytest
from django.contrib.auth.models import User
from django.core.validators import ValidationError
from django.urls import reverse

from cards.models import Deck
from users.managers import ProfileManager

pytestmark = pytest.mark.django_db


def test_default_deck_creation():
    user = User()
    user.username = 'newtestuser@example.com'
    user.email = 'newtestuser@example.com'
    user.set_password('testpassword')
    user.save()

    deck = Deck.objects.get_default(user)
    assert deck.title == 'main'
    assert deck.is_default is True


def test_user_get_by_user(client):
    response = client.get(reverse('users-get'))
    assert response.status_code == 401


def test_user_get_by_admin(admin_client):
    response = admin_client.get(reverse('users-get'))
    data = response.json()

    assert response.status_code == 200
    assert data == {
        'email': 'admin@example.com',
        'profile': {
            'is_verified': True
        }
    }


def test_user_verification_by_user(client):
    profile = User.objects.get(username='user@example.com').profile
    profile.verification_code = 'b' * 100
    profile.is_verified = False
    profile.save()

    data = json.dumps({'profile': 'a' * 60})
    url = reverse('users-verification')
    response = client.post(url, data=data, content_type="application/json")
    assert response.status_code == 400
    assert response.json() == {
        'non_field_errors': ['Invalid verification token']
    }

    data = json.dumps({'profile': 'b' * 100})
    url = reverse('users-verification')
    response = client.post(url, data=data, content_type="application/json")

    assert response.status_code == 200
    assert response.json() == {'status': True}
    profile.refresh_from_db()
    assert profile.is_verified is True
    assert profile.verification_code is None


def test_user_change_password_by_user(client):
    data = json.dumps({'password': '123456', 'password_two': '654321'})
    response = client.patch(reverse('users-password'),
                            data=data,
                            content_type="application/json")
    assert response.status_code == 401


def test_user_change_password_by_admin(admin_client):
    data = json.dumps({'password': '12345678', 'password_two': '87654321'})
    url = reverse('users-password')
    response = admin_client.patch(url,
                                  data=data,
                                  content_type="application/json")
    assert response.status_code == 400
    assert response.json() == {
        'password':
        ['This password is too common.', 'This password is entirely numeric.']
    }

    data = json.dumps({
        'password': 'hard120password',
        'password_two': 'hard121password'
    })
    response = admin_client.patch(url,
                                  data=data,
                                  content_type="application/json")
    assert response.status_code == 400
    assert response.json() == {'non_field_errors': ["Passwords don't match."]}

    data = json.dumps({
        'password': 'hard121password',
        'password_two': 'hard121password'
    })
    response = admin_client.patch(url,
                                  data=data,
                                  content_type="application/json")
    assert response.status_code == 200

    user = User.objects.get(username='admin')
    assert response.json() == {'status': True}
    assert user.check_password('hard121password') is True


def test_user_register_by_user(client, mailoutbox):
    """
    Test a new user registration
    """
    data = json.dumps({
        'email': 'admin@example.com',
        'password_new': 'password'
    })
    response = client.post(reverse('users-register'),
                           data=data,
                           content_type="application/json")
    assert response.status_code == 400
    assert response.json() == {
        'non_field_errors': [{
            'email': ['A user with that email already exists.']
        }]
    }

    data = json.dumps({'email': 'newuser@example.com', 'password_new': '12'})
    response = client.post(reverse('users-register'),
                           data=data,
                           content_type="application/json")

    assert response.status_code == 400
    assert response.json() == {
        'password': [
            'This password is too short. \
It must contain at least 8 characters.', 'This password is too common.',
            'This password is entirely numeric.'
        ]
    }

    data = json.dumps({
        'email': 'newuser@example.com',
        'password_new': 'super_password'
    })
    response = client.post(reverse('users-register'),
                           data=data,
                           content_type="application/json")

    assert response.status_code == 201
    json_data = response.json()
    user = User.objects.get(username='newuser@example.com')
    token = json_data['token']
    refresh = json_data['refresh']

    assert token is not None
    assert refresh is not None
    assert user.email == 'newuser@example.com'
    assert user.username == 'newuser@example.com'
    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.is_active is True
    assert user.check_password('super_password') is True

    response = client.post('/api-token-refresh/',
                           data={'refresh': refresh},
                           content_type="application/json")
    assert response.status_code == 200

    token = response.json()['access']
    refresh = json_data['refresh']
    assert token is not None
    assert refresh is not None

    response = client.get(reverse('api-root'))
    assert response.status_code == 401

    response = client.get(reverse('api-root'),
                          HTTP_AUTHORIZATION='JWT ' + token)
    assert response.status_code == 200
    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.recipients() == ['newuser@example.com']
    assert 'Welcome to Nativecards' in mail.subject
    assert 'Your registration was successful' in mail.alternatives[0][0]
    assert user.profile.verification_code in mail.alternatives[0][0]
    assert user.username in mail.alternatives[0][0]

    deck = Deck.objects.get_default(user)
    assert deck.title == 'main'
    assert deck.is_default is True


def test_user_register_validation_errors_by_user(client, mocker):
    """
    Test validation errors raised during the user registration
    """

    def raise_error(email: str, passowrd: str) -> None:
        raise ValidationError('test')

    ProfileManager.create_user = mocker.MagicMock(side_effect=raise_error)

    data = json.dumps({
        'email': 'newuser@example.com',
        'password_new': 'super_password'
    })
    response = client.post(reverse('users-register'),
                           data=data,
                           content_type="application/json")

    assert response.status_code == 400
    assert 'test' in str(response.content)


def test_user_admin_list_display(admin_client, mocker):
    """
    Test validation errors raised during the user registration
    """
    response = admin_client.post(reverse('admin:auth_user_changelist'))
    content = str(response.content)
    assert 'column-is_verified' in content
    assert 'icon-yes.svg' in content
