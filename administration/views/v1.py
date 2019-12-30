from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

import logging
logger = logging.getLogger(__name__)

from accounts import models as acc_models
from accounts.permissions import TokenOrSessionAuthentication
from administration.models import *
from administration.serializers import v1 as adm_ser_v1
from artist_portal.viewsets import GenericPlatformViewSet
from artist_portal._helpers import responses
from content import models as cnt_models

# -----------------------------------------------------------------------------

class FormViewSet(viewsets.GenericViewSet):
    queryset = ContactForm.objects.all()
    serializer_class = adm_ser_v1.ContactFormSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"]],
        "POST": [["ADMIN"],["first-party"]],
    }

    @action(detail=False, methods=['post'], url_path="contact-form", url_name="contact-form")
    def contact_form(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return responses.CREATED(serializer)
        else:
            return responses.SERIALIZER_ERROR_RESPONSE(serializer)
        return responses.NO_REQUEST_TYPE()


class CompanyViewSet(GenericPlatformViewSet):
    platform = 'Revibe'
    queryset = ContactForm.objects.all()
    serializer_class = adm_ser_v1.ContactFormSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"]]
    }

    @action(detail=False, methods=['get'], url_path='basic-metrics')
    def basic_metrics(self, request, *args, **kwargs):
        data = {}
        data['Users'] = {}
        data['Artists'] = {}
        data['Albums'] = {}
        data['Songs'] = {}

        data['Users']['Count'] = acc_models.CustomUser.objects.count()

        data['Artists']['Count'] = cnt_models.Artist.objects.filter(platform='Revibe').count()

        data['Albums']['Displayed'] = self.platform.Albums.count()
        data['Albums']['Hidden'] = self.platform.HiddenAlbums.count()
        data['Albums']['All'] = cnt_models.Album.objects.count()

        data['Songs']['Displayed'] = self.platform.Songs.count()
        data['Songs']['Hidden'] = self.platform.HiddenSongs.count()
        data['Songs']['All'] = cnt_models.Song.objects.count()

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='user-metrics', url_name="user_metrics")
    def user_metrics(self, request, *args, **kwargs):
        queryset = acc_models.CustomUser.objects.all()
        serializer_class = adm_ser_v1.UserMetricsSerializer

        data = {}
        data['User Count'] = queryset.count()

        serializer = serializer_class(queryset, many=True)
        data['Users'] = serializer.data

        return responses.OK(data=data)
