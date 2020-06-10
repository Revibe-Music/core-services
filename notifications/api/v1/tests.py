"""
Created: 10 June 2020
"""

from django.urls import reverse

from revibe._helpers.test import RevibeTestCase

from notifications.models import Notification
from notifications.utils.models.notification import create_notification_uuid

# -----------------------------------------------------------------------------


class EmailImageAttributionTestCase(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._get_external_event()
        self._get_external_event_template()

    def test_email_image_attribution(self):
        # create Notification
        tracking_id = create_notification_uuid()
        notif = Notification.objects.create(event_template=self.external_event_template, user=self.user, read_id=tracking_id)

        # configure request
        url = reverse('image-attribution', args=[tracking_id])

        # send request
        response = self.client.get(url, format="json")

        # validate response
        self.assert200(response)
        notif.refresh_from_db()
        self.assertTrue(
            notif.seen, 
            msg="Notification 'seen' field has not been changed"
        )
        self.assertTrue(
            bool(notif.date_seen),
            msg="The notification 'date_seen' field has not been updated"
        )


