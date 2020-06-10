"""
Created: 10 June 2020
"""

from django.utils import timezone

import uuid

from notifications.models import Notification

# -----------------------------------------------------------------------------


def mark_email_as_read(read_id, raise_exception: bool=False):
    """
    Take a read_id and mark that email as read
    """

    try:
        notifs = Notification.objects.filter(read_id=read_id, seen=False)

        # return if there are no notifications with this ID
        if not notifs.exists():
            return

        # get the notification
        notif = notifs.order_by('-date_created').first()

        # set the notification as seen and that it was seen now
        notif.seen = True
        notif.date_seen = timezone.now()
        notif.save()

    except Exception as e:
        if raise_exception:
            raise e
        else:
            pass

    return


def create_notification_uuid():
    """
    Generates a unique UUID for notifications.
    Will ensure that the UUID that is returned is not in use
    """
    new_uuid = None

    # set a check value to determine if the auto-generated UUID is in use
    in_use = True
    while in_use:
        # generate UUID
        new_uuid = uuid.uuid4()

        # check if that ID is in use
        notifs = Notification.objects.filter(read_id=new_uuid)

        in_use = notifs.exists()
    
    return new_uuid

