"""
Register Celery tasks that can be run asyncronously

Created: 19 May 2020
Author: Jordan Prechac
"""

from celery import shared_task

from accounts.models import CustomUser

from .core import Attributor

# -----------------------------------------------------------------------------


@shared_task
def weekly_email(active=True, inactive=True, new=True, *args, **kwargs):
    print("This function has been disabled")


@shared_task
def attribute_action(user_id, name, *args, **kwargs):
    user = CustomUser.objects.get(id=user_id)

    attributr = Attributor(user, name, *args, **kwargs)
    result = attributr.attribute()

    return result


