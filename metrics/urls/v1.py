from django.urls import path
from django.conf.urls import include
from rest_framework import routers

from metrics.views import v1

router = routers.DefaultRouter()
router.register("stream", v1.StreamView, "stream")

urlpatterns = [
    path("", include(router.urls)),
]

