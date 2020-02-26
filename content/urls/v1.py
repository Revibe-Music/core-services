from django.urls import path
from django.conf.urls import include
from rest_framework import routers

from content.views import v1

router = routers.DefaultRouter()
router.register('artist', v1.ArtistViewset, "artist")
router.register('album', v1.AlbumViewSet, "album")
router.register('song', v1.SongViewSet, "song")
router.register('search', v1.MusicSearch, "search")
router.register('browse', v1.Browse, 'browse')

urlpatterns = [
    path("", include(router.urls)),
]
