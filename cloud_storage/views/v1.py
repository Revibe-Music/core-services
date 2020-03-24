"""
Created: 24 Mar. 2020
Author: Jordan Prechac
"""

from rest_framework import viewsets

from revibe.pagination import CustomLimitOffsetPagination

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

