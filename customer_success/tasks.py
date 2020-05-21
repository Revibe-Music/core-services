"""
Register Celery tasks that can be run asyncronously

Created: 19 May 2020
Author: Jordan Prechac
"""

from celery import shared_task

from accounts.models import CustomUser
from administration.utils import retrieve_variable
from notifications.tasks import send_notification

from .core import Attributor

# -----------------------------------------------------------------------------


@shared_task
def weekly_email(active=True, inactive=True, new=True, *args, **kwargs):
    # determine which groups to send a notification to
    # groups = []
    # if active:
    #     groups.append('active')
    # if inactive:
    #     groups.append('inactive')
    # if new:
    #     groups.append('new')

    # expires = retrieve_variable('customer_success__weekly-email__task-expire-time', 60*60)
    # expires = int(expires)

    # triggers = {
    #     'active': retrieve_variable('customer_success__weekly-email__active-event', 'reminder-v1-active'),
    #     'inactive': retrieve_variable('customer_success__weekly-email__inactive-event', 'reminder-v1-inactive'),
    #     'new': retrieve_variable('customer_success__weekly-email__new-event', 'reminder-v1-new'),
    # }

    # for g in groups:
    #     user_ids = group_users(g, ids=True)
    #     trigger = triggers.get(g)
    #     for u in user_ids:
    #         send_notification \
    #             .s(u, trigger, *args, **kwargs) \
    #             .set(expires=expires) \
    #             .delay()

    print("This function has been disabled")


@shared_task
def attribute_action(user_id, name, *args, **kwargs):
    user = CustomUser.objects.get(id=user_id)

    attributr = Attributor(user, name, *args, **kwargs)
    result = attributr.attribute()

    return result


