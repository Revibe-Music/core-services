"""
Created: 03 June 2020
Author: Jordan Prechac
"""

from rest_framework import viewsets

from revibe._helpers import responses
from revibe.exceptions import api

from accounts.permissions import TokenOrSessionAuthentication
from notifications.decorators import notifier
from surveys.models import ArtistOfTheWeek

from .serializers import ArtistOfTheWeekSerializer

# -----------------------------------------------------------------------------


class ArtistOfTheWeekViewset(viewsets.ModelViewSet):
    serializer_class = ArtistOfTheWeekSerializer
    permission_classes = [TokenOrSessionAuthentication,]
    required_alternate_scopes = {
        'GET': [["ADMIN"], ["first-party", "artist"]],
        'POST': [["ADMIN"], ["first-party", "artist"]],
        'DELETE': [["ADMIN"], ["first-party", "artist"]]
    }

    def get_queryset(self):
        queryset = ArtistOfTheWeek.objects.filter(user=self.request.user)

        return queryset


    def update(self, request, pk=None, *args, **kwargs):
        raise api.ServiceUnavailableError("Applications cannot be edited. Please contact support@revibe.tech for more information.")

    def destroy(self, request, pk=None, *args, **kwargs):
        raise api.NotImplementedError("Cannot delete application right now. Please contact support@revibe.tech to remove the application.")


