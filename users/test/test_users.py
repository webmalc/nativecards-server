"""
The tests module for the users package
"""
import json

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from cards.models import Deck
from nativecards.models import Settings

pytestmark = pytest.mark.django_db  # pylint: disable=invalid-name


def test_default_deck_creation():
    """
    Should create a deck when creating a user
    """
    user = User()
    user.username = 'newtestuser@example.com'
    user.email = 'newtestuser@example.com'
    user.set_password('testpassword')
    user.save()

    deck = Deck.objects.get_default(user)
    assert deck.title == 'main'
    assert deck.is_default is True


def test_user_get_by_user(client):
    """
    Should return 401 error code for non authenticated users
    """
    response = client.get(reverse('users-get'))
    assert response.status_code == 401


def test_user_get_by_admin(admin_client):
    """
    Should return a user
    """
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
    """
    Should verify a user by a token
    """
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
    """
    Should return 401 error code for non authenticated users
    """
    data = json.dumps({'password': '123456', 'password_two': '654321'})
    response = client.patch(reverse('users-password'),
                            data=data,
                            content_type="application/json")
    assert response.status_code == 401


def test_user_change_password_by_admin(admin_client):
    """
    Should change password
    """
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
    def post(data: dict):
        return client.post(reverse('users-register'),
                           data=data,
                           content_type="application/json")

    data = json.dumps({
        'email': 'admin@example.com',
        'password_new': 'password',
        'language': 'xx',
    })
    response = post(data)
    assert response.status_code == 400
    assert response.json() == {
        'non_field_errors': [{
            'email': ['A user with that email already exists.']
        }]
    }

    data = json.dumps({
        'email': 'newuser@example.com',
        'password_new': '12',
        'language': 'xx',
    })
    response = post(data)
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
        'password_new': 'super_password',
        'language': 'xx',
    })
    response = post(data)
    assert response.status_code == 400
    assert response.json() == {
        'language': ["Value 'xx' is not a valid choice."]
    }

    data = json.dumps({
        'email': 'newuser@example.com',
        'password_new': 'super_password',
        'language': 'es',
    })
    response = post(data)
    assert response.status_code == 201
    json_data = response.json()
    user = User.objects.get(username='newuser@example.com')
    token = json_data['token']
    refresh = json_data['refresh']
    settings = Settings.objects.get(created_by=user)

    assert token is not None
    assert refresh is not None
    assert settings.language == 'es'
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
    refresh = response.json()['refresh']
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


def test_admin_jwt_token(client, admin):
    """
    Should authenticate by the JWT token
    """
    admin.set_password('password')
    admin.save()

    response = client.post('/api-token-auth/',
                           data={
                               'username': admin.username,
                               'password': 'password'
                           },
                           content_type="application/json")

    assert response.status_code == 200
    token = response.json()['access']
    refresh = response.json()['refresh']
    assert token is not None
    assert refresh is not None

    response = client.post(reverse('decks-list'),
                           data={
                               "title": "new deck",
                               "description": 'new deck description',
                           },
                           content_type="application/json",
                           HTTP_AUTHORIZATION='JWT ' + token)

    assert response.status_code == 201
    assert response.json()['created_by'] == 'admin'
    assert response.json()['title'] == 'new deck'


def test_user_admin_list_display(admin_client):
    """
    Test validation errors raised during the user registration
    """
    response = admin_client.post(reverse('admin:auth_user_changelist'))
    content = str(response.content)
    assert 'column-is_verified' in content
    assert 'icon-yes.svg' in content
