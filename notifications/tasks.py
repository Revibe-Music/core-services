"""
Created: 08 May 2020
Author: Jordan Prechac
"""

from celery import shared_task

from accounts.models import CustomUser
from .core import Notifier

# -----------------------------------------------------------------------------

@shared_task
def send_notification(user_id, trigger, *args, **kwargs):
    user = CustomUser.objects.get(id=user_id)

    notifier = Notifier(user, trigger, *args, **kwargs)
    result = notifier.send()

    return result


