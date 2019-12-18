from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from music.views import v1

router = routers.DefaultRouter()
router.register("library", v1.LibraryViewSet, "library")
router.register("playlist", v1.PlaylistViewSet, "playlist")

urlpatterns = [
    path("", include(router.urls)),
    # path("search/", views.MusicSearch.as_view({"get": "search"}), "music_search"),
]
