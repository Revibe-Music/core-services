from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from music.views import v1

router = routers.DefaultRouter()
router.register("artist", v1.ArtistViewSet, "artist")
router.register("album", v1.AlbumViewSet, "album")
router.register("song", v1.SongViewSet, "song")
router.register("library", v1.LibraryViewSet, "library")
router.register("songcontrib", v1.SongContributorViewSet, "songcontrib")
router.register("playlist", v1.PlaylistViewSet, "playlist")
router.register("search", v1.MusicSearch, "music_search")

urlpatterns = [
    path("", include(router.urls)),
    # path("search/", views.MusicSearch.as_view({"get": "search"}), "music_search"),
]
