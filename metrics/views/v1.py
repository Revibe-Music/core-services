from django.conf import settings
from rest_framework.views import APIView

from revibe._errors.network import ExpectationFailedError
from revibe._helpers import responses
from revibe.pagination import CustomLimitOffsetPagination
from revibe.viewsets import *

from accounts.permissions import TokenOrSessionAuthentication
from metrics.models import *
from metrics.serializers.v1 import *

# -----------------------------------------------------------------------------

class StreamView(PlatformViewSet):
    platform = 'Revibe'
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer
    pagination_class = CustomLimitOffsetPagination
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "POST": [["ADMIN"],["first-party"]],
    }

    def create(self, request, *args, **kwargs):
        """
        Overwrites the default create method simply to send a blank 201 response
        """
        super().create(request, *args, **kwargs)
        return responses.CREATED()


