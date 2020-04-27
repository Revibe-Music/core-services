from django.urls import reverse

from revibe._helpers import status
from revibe._helpers.test import RevibeTestCase

# -----------------------------------------------------------------------------

class TestStreamViewset(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._create_song()

    def test_record_stream(self):
        # configure test
        url = "/v1/metrics/stream/"

        data = {
            "song_id": str(self.content_song.id),
            "stream_duration": int(self.content_song.duration - 1),
            "is_downloaded": False,
            "is_saved": False
        }

        # send the request
        response = self.client.post(url, data, format="json", **self._get_headers())

        # validate the response
        self.assert201(response)


