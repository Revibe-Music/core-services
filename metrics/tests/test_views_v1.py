from django.urls import reverse

from logging import getLogger
logger = getLogger(__name__)

from revibe._helpers import status
from revibe._helpers.test import RevibeTestCase

# -----------------------------------------------------------------------------

class TestStreamViewset(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
    
    def test_failed_streaming(self):
        # expect to fail because we are not testing in the cloud
        url = reverse('streams')

        data = {}

        response = self.client.post(url, data, format="json", **self._get_headers())

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

