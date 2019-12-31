from rest_framework import serializers

import logging
logger = logging.getLogger(__name__)

from accounts import models as acc_models
from accounts.serializers.v1 import UserSerializer
from administration.models import *
from content import models as cnt_models

# -----------------------------------------------------------------------------

class ContactFormSerializer(serializers.ModelSerializer):

    subject = serializers.CharField(required=True)
    message = serializers.CharField(required=True)

    # read-only
    id = serializers.IntegerField(read_only=True)
    user = UserSerializer(read_only=True)
    resolved = serializers.BooleanField(read_only=True)
    assigned_to = serializers.BooleanField(read_only=True)

    # write-only
    user_id = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = ContactForm
        fields = [
            'subject',
            'message',

            # read-only
            'id',
            'user',
            'resolved',
            'assigned_to',

            # write-only
            'user_id'
        ]


class UserMetricsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    last_login = serializers.ReadOnlyField()
    is_staff = serializers.ReadOnlyField()
    date_joined = serializers.ReadOnlyField()

    class Meta:
        model = acc_models.CustomUser
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'last_login',
            'is_staff',
            'date_joined',
            'artist_id',
        ]


class ArtistMetricsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    uri = serializers.ReadOnlyField()
    ext = serializers.SerializerMethodField('image_ext', read_only=True)
    name = serializers.ReadOnlyField()
    date_joined = serializers.ReadOnlyField()
    user_id = serializers.SerializerMethodField('get_user_id', read_only=True)

    class Meta:
        model = cnt_models.Artist
        fields = [
            'id',
            'uri',
            'ext',
            'name',
            'date_joined',
            'user_id',
        ]
    
    def image_ext(self, obj):
        if obj.image:
            return obj.image.name.split('.')[-1]
        else:
            return None
    
    def get_user_id(self, obj):
        if hasattr(obj, 'artist_user'):
            return obj.artist_user.id
        else:
            return None


class AlbumMetricsSerializer(serializers.ModelSerializer):

    ext = serializers.SerializerMethodField('image_ext', read_only=True)
    artist_id = serializers.SerializerMethodField('get_artist_id', read_only=True)

    class Meta:
        model = cnt_models.Album
        fields = [
            'id',
            'uri',
            'ext',
            'name',
            'type',
            'uploaded_date',
            'last_changed',
            'date_published',
            'is_displayed',
            'is_deleted',
            'artist_id',
        ]

    def image_ext(self, obj):
        if obj.image:
            return obj.image.name.split('.')[-1]
        else:
            return None
    
    def get_artist_id(self, obj):
        if hasattr(obj, 'uploaded_by'):
            return obj.uploaded_by.id
        else:
            return None

