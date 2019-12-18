from django.urls import path
from django.conf.urls import include
from rest_framework import routers

from content.views import v1

router = routers.DefaultRouter()
router.register('artist', v1.ArtistViewset, "artist")

urlpatterns = [
    path("", include(router.urls)),
]
