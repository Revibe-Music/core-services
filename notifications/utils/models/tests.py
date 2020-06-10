"""
Created: 10 June 2020
"""

from revibe._helpers.test import RevibeTestCase

from notifications.models import Notification
from notifications.utils.models.notification import create_notification_uuid, mark_email_as_read

# -----------------------------------------------------------------------------


class NotificationUtilsTestCase(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()

        self._get_external_event()
        self._get_external_event_template()

    def test_create_notification_uuid(self):
        # create notifications with IDs
        pass

    def test_mark_email_as_read(self):
        # create notification
        notif_tracking_id = create_notification_uuid()
        Notification.objects.create(event_template=self.external_event_template, user=self.user, read_id=notif_tracking_id)

        # call function
        mark_email_as_read(notif_tracking_id)

        # check stuff
        notif = Notification.objects.get(read_id=notif_tracking_id)
        self.assertTrue(
            notif.seen,
            msg="Notification 'seen' field has not been changed"
        )
        self.assertEqual(
            bool(notif.date_seen), True,
            msg="The notification 'date_seen' field has not been updated"
        )



