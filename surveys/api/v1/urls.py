"""
Created: 03 June 2020
Author: Jordan Prechac
"""

from django.urls import path, include
from rest_framework import routers

from . import views

# -----------------------------------------------------------------------------


router = routers.DefaultRouter()
router.register("artistoftheweek", views.ArtistOfTheWeekViewset, "artistoftheweek-application")


urlpatterns = [
    path("", include(router.urls)),
]
