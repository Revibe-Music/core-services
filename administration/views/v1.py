from django.db.models import Exists
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

import datetime
import random

import logging
logger = logging.getLogger(__name__)

from revibe.pagination import CustomLimitOffsetPagination
from revibe.sharing import mobile_app_sharing_link
from revibe.viewsets import GenericPlatformViewSet
from revibe.utils.params import get_url_param
from revibe._errors import network
from revibe._errors.data import NoKeysError
from revibe._errors.random import ValidationError
from revibe._helpers import const, responses

from accounts import models as acc_models
from accounts.permissions import TokenOrSessionAuthentication, AdminOnlyTokenPermissions
from administration.models import *
from administration.serializers import v1 as adm_ser_v1
from administration.utils.models import see_alert
from content import models as cnt_models
from metrics.models import Stream

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
        serializer = self.get_serializer(data=request.data, *args, **kwargs)
        if serializer.is_valid():
            try:
                serializer.save()
            except ValidationError as err:
                raise network.BadRequestError(str(err))
            return responses.CREATED(serializer=serializer)
        else:
            raise network.BadRequestError(serializer.errors)
        return responses.NO_REQUEST_TYPE()


class YouTubeKeyViewSet(viewsets.GenericViewSet):
    queryset = YouTubeKey.objects.filter()
    serializer_class = adm_ser_v1.YouTubeKeySerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]],
    }

    def list(self, request, *args, **kwargs):
        # get the key with the most points
        choices = YouTubeKey.objects.order_by('-points_per_user')
        if len(choices) == 0:
            raise NoKeysError()

        params = request.query_params
        old_key = get_url_param(params, "old_key")
        if old_key != None:
            try:
                old_key_object = YouTubeKey.objects.get(key=str(old_key))
                old_key_object.last_date_broken = datetime.date.today()
                old_key_object.number_of_users -= 1
                old_key_object.save()

                choices = choices.exclude(key=str(old_key))
            except Exception as e:
                raise e

        # loop through the keys in order to see if they are valid
        i = 0
        while i < len(choices):
            choice = choices[i]
            
            if not choice.is_valid:
                i += 1
                continue
            
            # return the key, and add to the number of users
            choice.number_of_users += 1
            choice.save()
            return responses.OK(data={'key': str(choice.key)})
        
        raise NoKeysError("Could identify any valid keys")


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.display_objects.all()
    serializer_class = adm_ser_v1.AlertSerializer
    permission_classes = [TokenOrSessionAuthentication]
    pagination_class = CustomLimitOffsetPagination
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]],
        "POST": [["ADMIN"],["first-party"]]
    }

    def get_queryset(self):
        alerts = Alert.display_objects.exclude(users_seen=self.request.user)

        return alerts

    def create(self, request, *args, **kwargs):
        user = self.request.user
        alert = Alert.objects.get(id=request.data["alert_id"])
        see_alert(user, alert)

        return responses.CREATED()


class CompanyViewSet(GenericPlatformViewSet):
    platform = 'Revibe'
    queryset = ContactForm.objects.all()
    serializer_class = adm_ser_v1.ContactFormSerializer
    permission_classes = [AdminOnlyTokenPermissions]
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
    
    @action(detail=False, methods=['get'], url_path="campaign-metrics", url_name="campaign-metrics")
    def campaign_metrics(self, request, *args, **kwargs):
        queryset = Campaign.objects.all()
        serializer_class = adm_ser_v1.CampaignMetricsSerializer

        data = {}
        data['Campaign Count'] = queryset.count()

        serializer = serializer_class(queryset, many=True)
        data['Campaigns'] = serializer.data

        return responses.OK(data=data)


    @action(detail=False, methods=['get'], url_path="stream-metrics", url_name="stream-metrics")
    def stream_metrics(self, request, *args, **kwargs):
        queryset = Stream.metrics_objects.filter(song__isnull=False)
        serializer_class = adm_ser_v1.StreamMetricsSerializer

        data = {}
        data['Stream Count'] = queryset.count()

        serializer = serializer_class(queryset, many=True)
        data['Streams'] = serializer.data

        return responses.OK(data=data)


class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.display_objects.all()
    serializer_class = adm_ser_v1.BlogSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = CustomLimitOffsetPagination
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]],
    }


class StateVariablesView(viewsets.GenericViewSet):
    queryset = Variable.objects.all()
    serializer_class = None
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"], ["first-party"]]
    }

    def list(self, request, *args, **kwargs):
        user = request.user

        variables = {
            "share_text": mobile_app_sharing_link(user),
        }

        return responses.OK(data=variables)

