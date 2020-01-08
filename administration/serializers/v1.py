from rest_framework import serializers

import logging
logger = logging.getLogger(__name__)

from revibe._errors.random import ValidationError

from accounts import models as acc_models
from administration.models import *
from content import models as cnt_models

# -----------------------------------------------------------------------------

class ContactFormSerializer(serializers.ModelSerializer):

    subject = serializers.CharField(required=True)
    message = serializers.CharField(required=True)

    # read-only
    id = serializers.IntegerField(read_only=True)
    resolved = serializers.BooleanField(read_only=True)
    assigned_to = serializers.BooleanField(read_only=True)

    # write-only
    user_id = serializers.CharField(required=False, write_only=True)
    first_name = serializers.CharField(required=False, write_only=True)
    last_name = serializers.CharField(required=False, write_only=True)
    email = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = ContactForm
        fields = [
            'subject',
            'message',

            # read-only
            'id',
            'resolved',
            'assigned_to',

            # write-only
            'user_id',
            'first_name',
            'last_name',
            'email',
        ]
    
    def create(self, validated_data, *args, **kwargs):
        contact_form_data = {
            'subject':validated_data['subject'],
            'message':validated_data['message'],
        }

        # check that some form of personal identifier is in the form
        name_fields = ['first_name','last_name','email']
        name_data = True
        for f in name_fields:
            if f not in validated_data.keys():
                name_data = False
        
        # raise exception if the data does not have a user or name fields
        if not (('user_id' in validated_data.keys()) or name_data):
            raise ValidationError("Contact form must contain some form of identifiable information: \
                user_id, or name and email ")

        if 'user_id' in validated_data.keys():
            user = acc_models.CustomUser.objects.get(id=validated_data['user_id'])
            contact_form_data['user'] = user
        else:
            contact_form_data['first_name'] = validated_data['first_name']
            contact_form_data['last_name'] = validated_data['last_name']
            contact_form_data['email'] = validated_data['email']
        
        contact_form = ContactForm(**contact_form_data)
        contact_form.save()

        logger.info("Contact form created.")

        return contact_form


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
        if hasattr(obj, 'uploaded_by') and (obj.uploaded_by != None):
            return obj.uploaded_by.id
        else:
            return None


class SongMetricsSerializer(serializers.ModelSerializer):

    ext = serializers.SerializerMethodField('get_ext', read_only=True)
    album_id = serializers.ReadOnlyField(source='album.id')
    artist_id = serializers.ReadOnlyField(source='uploaded_by.id')

    class Meta:
        model = cnt_models.Song
        fields = [
            'id',
            'uri',
            'ext',
            'title',
            'genre',
            'duration',
            'is_explicit',

            'is_displayed',
            'is_deleted',
            'last_changed',
            'uploaded_date',

            'album_id',
            'artist_id',
        ]
    
    def get_ext(self, obj):
        if hasattr(obj, 'file') and (obj.file != None):
            return obj.file.name.split('.')[-1]
        else:
            return None

