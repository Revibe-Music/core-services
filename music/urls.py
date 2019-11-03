from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from . import views

urlpatterns = [
    path("artists/", views.ArtistViewSet),
    path("albums/", views.AlbumViewSet),
]
