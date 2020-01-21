"""
The users mailer module
"""
from django.contrib.auth.models import User
from nativecards.lib.messengers import mailer


def send_registration_email(user: User) -> None:
    """
    Send the registration to the user
    """
    mailer.mail_user(subject='Welcome to Nativecards',
                     template='emails/registration.html',
                     data={
                         'url': user.profile.verification_code,
                         'username': user.username
                     },
                     user=user)
