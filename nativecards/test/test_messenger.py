import pytest
from django.contrib.auth.models import User

from nativecards.lib.messengers import mailer

pytestmark = pytest.mark.django_db


def test_mail_managers(mailoutbox):
    mailer.mail_managers(subject='Text message', data={'text': 'Test text'})
    assert len(mailoutbox) == 1
    mail = mailoutbox[0]

    assert mail.recipients() == ['admin@example.com', 'manager@example.com']
    assert 'Text message' in mail.subject
    assert 'Test text' in mail.alternatives[0][0]


def test_mail_client_by_email(mailoutbox):
    mailer.mail_user(subject='Test message',
                     template='emails/registration.html',
                     data={},
                     email='client@example.com')

    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.recipients() == ['client@example.com']
    assert 'Test message' in mail.subject
    assert 'Your registration was successful' in mail.alternatives[0][0]


def test_mail_client_by_client(mailoutbox):
    def send(user):
        user = User.objects.get(username=user)
        mailer.mail_user(subject='Test message',
                         template='emails/registration.html',
                         data={},
                         user=user)

    send('admin')
    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.recipients() == ['admin@example.com']
    assert 'Test message' in mail.subject
    assert 'Your registration was successful' in mail.alternatives[0][0]
