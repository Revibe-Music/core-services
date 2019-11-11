from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register("artists", views.ArtistViewSet, "artists")
router.register("albums", views.AlbumViewSet, "albums")
router.register("songs", views.SongViewSet, "songs")

urlpatterns = [
    path("", include(router.urls)),
]
