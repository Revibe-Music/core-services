"""
Register Celery tasks that can be run asyncronously

Created: 19 May 2020
Author: Jordan Prechac
"""

from celery import shared_task

from accounts.models import CustomUser

from .core import Attributor
from .core.weekly_email import send_weekly_email

# -----------------------------------------------------------------------------


@shared_task
def weekly_email(run_async=True):
    return send_weekly_email(run_async=run_async)


@shared_task
def attribute_action(user_id, name, *args, **kwargs):
    user = CustomUser.objects.get(id=user_id)

    attributr = Attributor(user, name, *args, **kwargs)
    result = attributr.attribute()

    return result


