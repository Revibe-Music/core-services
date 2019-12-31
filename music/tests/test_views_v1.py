from django.urls import reverse
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict

from logging import getLogger
logger = getLogger(__name__)

from artist_portal._helpers import status
from artist_portal._helpers.test import AuthorizedContentAPITestCase

# -----------------------------------------------------------------------------


class TestLibrary(AuthorizedContentAPITestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._create_song()
    
    def test_list_libraries(self):
        url = reverse('library-list')
        response = self.client.get(url, format="json", **self._get_headers())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.data), ReturnList)
        self.assertEqual(len(response.data), 2)
    
    def test_save_song(self):
        url = reverse('library-songs')
        data = {
            "platform": "Revibe",
            "song_id": self.song.id
        }
        response = self.client.post(url, data, format="json", **self._get_headers())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(type(response.data), ReturnDict)
        self.assertEqual(response.data['song'], str(self.song.id))

