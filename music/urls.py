from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register("artists", views.ArtistViewSet, "artists")
router.register("albums", views.ArtistViewSet, "albums")

urlpatterns = [
    path("", include(router.urls)),
]
