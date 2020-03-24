"""
Created: 24 Mar. 2020
Author: Jordan Prechac
"""

from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from cloud_storage.views import v1

# -----------------------------------------------------------------------------

router = routers.DefaultRouter()
router.register("me", v1.FileViewSet, "me")

urlpatterns = [
    path("", include(router.urls))
]
