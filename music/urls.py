from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register("artist", views.ArtistViewSet, "artist")
router.register("album", views.AlbumViewSet, "album")
router.register("song", views.SongViewSet, "song")
router.register("library", views.LibraryViewSet, "library")
router.register("songcontrib", views.SongContributorViewSet, "songcontrib")
router.register("library_songs", views.LibrarySongViewSet, "library_songs")

urlpatterns = [
    path("", include(router.urls)),
]
