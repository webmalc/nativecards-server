"""
The mailer module
"""
import logging

from django.conf import settings
from django.core.mail import mail_managers as base_mail_managers
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _


def mail_managers(subject, data=None, template='emails/base_manager.html'):
    """
    Sends an email to the managers
    """
    base_mail_managers(
        subject=subject,
        message='',
        html_message=render_to_string(template, data if data else {}),
    )
    logging.getLogger('nativecards').info(
        'Send mail to managers. Subject: %s',
        subject,
    )


def mail_user(subject, template, data, email=None, user=None):
    """
    Sends an email to an user
    """
    send_mail(
        recipient_list=[email] if email else [user.email],
        from_email=settings.DEFAULT_FROM_EMAIL,
        subject=f'{settings.EMAIL_SUBJECT_PREFIX}{_(subject)}',
        message='',
        html_message=render_to_string(template, data),
    )

    logging.getLogger('nativecards').info(
        'Send mail to user. Subject: %s; user: %s; email: %s;',
        subject,
        user,
        email,
    )
