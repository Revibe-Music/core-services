"""
Created: 24 Mar. 2020
Author: Jordan Prechac
"""

from rest_framework import viewsets
from rest_framework.decorators import action

from revibe.pagination import CustomLimitOffsetPagination
from revibe._helpers import responses

from accounts.permissions import TokenOrSessionAuthentication
from cloud_storage.models import File
from cloud_storage.serializers import v1 as cst_ser_v1

# -----------------------------------------------------------------------------


class FileViewSet(viewsets.ModelViewSet):
    serializer_class = cst_ser_v1.FileSerializer
    pagination_class = CustomLimitOffsetPagination
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]],
        "POST": [["ADMIN"], ["first-party"]],
        "PATCH": [["ADMIN"],["first-party"]],
        "DELETE": [["ADMIN"],["first-party"]],
    }

    def get_queryset(self):
        artist = self.request.user.artist
        return File.objects.filter(owner=artist)

    @action(detail=False, methods=['get'], url_path="shared", url_name="shared")
    def shared_files(self, request, *args, **kwargs):
        artist = self.request.user.artist

        files = File.objects.filter(shared_with=artist).distinct()

        return responses.OK(serializer=cst_ser_v1.FileSerializer(files, many=True))
