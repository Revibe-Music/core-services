from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

import logging
logger = logging.getLogger(__name__)

from revibe.viewsets import GenericPlatformViewSet
from revibe._errors.random import ValidationError
from revibe._helpers import const, responses

from accounts import models as acc_models
from accounts.permissions import TokenOrSessionAuthentication
from administration.models import *
from administration.serializers import v1 as adm_ser_v1
from content import models as cnt_models

# -----------------------------------------------------------------------------

class FormViewSet(viewsets.GenericViewSet):
    queryset = ContactForm.objects.all()
    serializer_class = adm_ser_v1.ContactFormSerializer
    permission_classes = [permissions.AllowAny]
    required_alternate_scopes = {
        "GET": [["ADMIN"]],
        "POST": [["ADMIN"],["first-party"]],
    }

    @action(detail=False, methods=['post'], url_path="contact-form", url_name="contact-form")
    def contact_form(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except ValidationError as err:
                return responses.SERIALIZER_ERROR_RESPONSE(detail=str(err))
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

    @action(detail=False, methods=['get'], url_path='basic-metrics', url_name="basic-metrics")
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

    @action(detail=False, methods=['get'], url_path='user-metrics', url_name="user-metrics")
    def user_metrics(self, request, *args, **kwargs):
        queryset = acc_models.CustomUser.objects.all()
        serializer_class = adm_ser_v1.UserMetricsSerializer

        data = {}
        data['User Count'] = queryset.count()

        serializer = serializer_class(queryset, many=True)
        data['Users'] = serializer.data

        return responses.OK(data=data)
    
    @action(detail=False, methods=['get'], url_path="artist-metrics", url_name="artist-metrics")
    def artist_metrics(self, request, *args, **kwargs):
        queryset = cnt_models.Artist.objects.filter(platform=const.REVIBE_STRING)
        serializer_class = adm_ser_v1.ArtistMetricsSerializer

        data = {}
        data['Artist Count'] = queryset.count()

        serializer = serializer_class(queryset, many=True)
        data['Artists'] = serializer.data

        return responses.OK(data=data)

    @action(detail=False, methods=['get'], url_path="album-metrics", url_name="album-metrics")
    def album_metrics(self, request, *args, **kwargs):
        queryset = cnt_models.Album.objects.filter(platform=const.REVIBE_STRING)
        serializer_class = adm_ser_v1.AlbumMetricsSerializer

        data = {}
        data['Album Count'] = queryset.count()

        serializer = serializer_class(queryset, many=True)
        data['Albums'] = serializer.data

        return responses.OK(data=data)
    
    @action(detail=False, methods=['get'], url_path='song-metrics', url_name="song-metrics")
    def song_metrics(self, request, *args, **kwargs):
        queryset = cnt_models.Song.objects.filter(platform=const.REVIBE_STRING)
        serializer_class = adm_ser_v1.SongMetricsSerializer

        data = {}
        data['Song Count'] = queryset.count()

        serializer = serializer_class(queryset, many=True)
        data['Songs'] = serializer.data

        return responses.OK(data=data)

    @action(detail=False, methods=['get'], url_path="contact-form-metrics", url_name="contact-form-metrics")
    def contact_form_metrics(self, request, *args, **kwargs):
        queryset = ContactForm.objects.all()
        serializer_class = adm_ser_v1.ContactFormMetricsSerializer

        data = {}
        data['Contact Form Count'] = queryset.count()

        serializer = serializer_class(queryset, many=True)
        data['Contact Forms'] = serializer.data

        return responses.OK(data=data)
