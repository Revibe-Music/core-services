from django.urls import reverse
from rest_framework.test import APIClient

from logging import getLogger
logger = getLogger(__name__)

from revibe._helpers.test import BaseRevibeTestCase

# -----------------------------------------------------------------------------

class TestHealthView(BaseRevibeTestCase):
    def test_health(self):
        url = reverse('health_check')

        response = self.client.get(url, format="json")

        self.assert200(response.status_code)
        logger.info(f"Health check passed with status {response.status_code}")

