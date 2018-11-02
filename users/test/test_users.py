import json

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

pytestmark = pytest.mark.django_db


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


def test_user_register_by_user(admin_client, client, mailoutbox):
    data = json.dumps({
        'email': 'admin@example.com',
        'password_new': 'password'
    })
    response = admin_client.post(
        reverse('users-register'), data=data, content_type="application/json")
    assert response.status_code == 400
    assert response.json() == [{
        'email': ['A user with that email already exists.']
    }]

    data = json.dumps({'email': 'newuser@example.com', 'password_new': '12'})
    response = admin_client.post(
        reverse('users-register'), data=data, content_type="application/json")

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
    response = admin_client.post(
        reverse('users-register'), data=data, content_type="application/json")

    assert response.status_code == 201
    json_data = response.json()
    user = User.objects.get(username='newuser@example.com')
    token = json_data['token']

    assert token is not None
    assert json_data['token'] is not None
    assert user.email == 'newuser@example.com'
    assert user.username == 'newuser@example.com'
    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.is_active is True
    assert user.check_password('super_password') is True

    response = client.post(
        '/api-token-refresh/',
        data={'token': token},
        content_type="application/json")
    assert response.status_code == 200
    token = response.json()['token']
    assert token is not None

    response = client.get(reverse('api-root'))
    assert response.status_code == 401

    response = client.get(
        reverse('api-root'), HTTP_AUTHORIZATION='JWT ' + token)
    assert response.status_code == 200
    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.recipients() == ['newuser@example.com']
    assert 'Welcome to Nativecards' in mail.subject
    assert 'Your registration was successful' in mail.alternatives[0][0]
    assert user.profile.verification_code in mail.alternatives[0][0]
    assert user.username in mail.alternatives[0][0]
