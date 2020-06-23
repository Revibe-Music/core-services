"""
Created: 08 May 2020
Author: Jordan Prechac
"""

from __future__ import absolute_import

from django.apps import apps
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task

import datetime

# from accounts.models import CustomUser
from notifications.core import Notifier
from notifications.core.recap import send_artist_recap_email

CustomUser = apps.get_model('accounts', 'CustomUser')

# -----------------------------------------------------------------------------

@shared_task
def send_notification(user_id, trigger, *args, **kwargs):
    # from accounts.models import CustomUser
    # from notifications.core.notifier import Notifier


    user = CustomUser.objects.get(id=user_id)

    notifier = Notifier(user, trigger, *args, **kwargs)
    result = notifier.send()

    return result

@shared_task
def test_send_notification():
    """
    Sends an email to 
    """
    to_address = "jordanprechac@revibe.tech"
    subject = "Celery Beat Confirmation"
    message = f"If you are reading this email then Celery Beat is working in environment'{settings.ENV}' .\n\n" + \
        f"Execution time: {datetime.datetime.now()}"
    from_email = "noreply@revibe.tech"

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[to_address,]
    )

    return


@shared_task
def artist_recap_email(weeks=1):
    """
    """
    # from accounts.models import CustomUser
    # from notifications.core.recap import send_artist_recap_email

    artists = CustomUser.registered_objects.filter(
        artist__isnull=False, # they must be an artist
        profile__allow_email_reminders=True, profile__allow_email_notifications=True # they must allow notifications
    )

    for artist in artists:
        try:
            send_artist_recap_email(artist, weeks=weeks)
        except Exception as e:
            print(e)

