"""
Created: 08 May 2020
Author: Jordan Prechac
"""

from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task

import datetime

from accounts.models import CustomUser
from .core import Notifier

# -----------------------------------------------------------------------------

@shared_task
def send_notification(user_id, trigger, *args, **kwargs):
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

