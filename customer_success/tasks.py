"""
Register Celery tasks that can be run asyncronously

Created: 19 May 2020
Author: Jordan Prechac
"""

from __future__ import absolute_import

from celery import shared_task

from accounts.models import CustomUser

from .core import Attributor
from .core.weekly_email import send_weekly_email

# -----------------------------------------------------------------------------


@shared_task
def weekly_email(run_async=True):
    # from customer_success.core.weekly_email import send_weekly_email
    return send_weekly_email(run_async=run_async)


@shared_task
def attribute_action(user_id, name, *args, **kwargs):
    # from accounts.models import CustomUser
    # from customer_success.core import Attributor

    user = CustomUser.objects.get(id=user_id)

    attributr = Attributor(user, name, *args, **kwargs)
    result = attributr.attribute()

    return result


