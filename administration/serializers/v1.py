from rest_framework import serializers

import logging
logger = logging.getLogger(__name__)

from revibe._errors import network
from revibe._errors.random import ValidationError

from accounts import models as acc_models
from administration.models import *
from content import models as cnt_models
from metrics.models import Stream

# -----------------------------------------------------------------------------

class ContactFormSerializer(serializers.ModelSerializer):

    subject = serializers.CharField(required=True)
    message = serializers.CharField(required=True)

    # read-only
    id = serializers.IntegerField(read_only=True)
    resolved = serializers.BooleanField(read_only=True)
    assigned_to = serializers.BooleanField(read_only=True)
    date_created = serializers.ReadOnlyField()
    last_changed = serializers.ReadOnlyField()

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
            'date_created',
            'last_changed',

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
        
        user_id = validated_data.get('user_id', None)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
        if user != None and not user.is_anonymous:
            user_id = user.id
        
        # raise exception if the data does not have a user or name fields
        if not (bool(user_id) or name_data):
            raise ValidationError("Contact form must contain some form of identifiable information: \
                user_id, or name and email ")

        if bool(user_id):
            user = acc_models.CustomUser.objects.get(id=user_id)
            contact_form_data['user'] = user
        else:
            contact_form_data['first_name'] = validated_data['first_name']
            contact_form_data['last_name'] = validated_data['last_name']
            contact_form_data['email'] = validated_data['email']
        
        contact_form = ContactForm(**contact_form_data)
        contact_form.save()

        logger.info("Contact form created.")

        return contact_form


class YouTubeKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeKey
        fields = [
            'key'
        ]


class AlertSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alert
        fields = [
            "id",
            "subject",
            "message",
            "category",
            "start_date",
        ]

    def create(self, validated_data):
        raise network.BadEnvironmentError("Cannot create an alert from the API")
    
    def update(self, validated_data):
        raise network.BadEnvironmentError("Cannot update an alert from the API")


class BlogSerializer(serializers.ModelSerializer):
    class BlogTagSerializer(serializers.ModelSerializer):
        class Meta:
            model = BlogTag
            fields = ['text']

    author = serializers.SerializerMethodField('author_name', read_only=True)
    tags = BlogTagSerializer(read_only=True, many=True)

    class Meta:
        model = Blog
        fields = [
            'id',
            'title',
            'body',
            'summary',
            'publish_date',
            'header_image',
            'side_image',
            'display_style',
            'tags',
            'author',
        ]
    
    def author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}"

    def create(self, validated_data):
        raise network.BadEnvironmentError("Cannot create a blog post from the API")

    def update(self, validated_data):
        raise network.BadEnvironmentError("Cannot update a blog post from the API")


# metrics information

class UserMetricsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    last_login = serializers.ReadOnlyField()
    is_staff = serializers.ReadOnlyField()
    date_joined = serializers.ReadOnlyField()

    # profile information
    campaign = serializers.SerializerMethodField(method_name='get_campaign', read_only=True)
    referrer = serializers.SerializerMethodField(method_name='get_referrer', read_only=True)
    country = serializers.SerializerMethodField(method_name='_get_country', read_only=True)
    state = serializers.SerializerMethodField(method_name='_get_state', read_only=True)
    city = serializers.SerializerMethodField(method_name='_get_city', read_only=True)
    zip_code = serializers.SerializerMethodField(method_name='_get_zip_code', read_only=True)

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

            # profile information
            'referrer',
            'campaign',
            'country',
            'state',
            'city',
            'zip_code',
        ]

    def _get_profile(self, obj):
        return getattr(obj, 'profile', None)
    
    def get_referrer(self, obj):
        profile = self._get_profile(obj)
        if profile == None:
            return None
        referrer = getattr(profile, 'referrer', None)
        if referrer == None:
            return None
        return getattr(referrer, 'id', None)    
    def get_campaign(self, obj):
        profile = self._get_profile(obj)
        if profile == None:
            return None
        campaign = getattr(profile, 'campaign', None)
        if campaign == None:
            return None
        return getattr(campaign, 'id', None)
    def _get_country(self, obj):
        profile = self._get_profile(obj)
        return getattr(profile, "country", None)
    def _get_state(self, obj):
        profile = self._get_profile(obj)
        return getattr(profile, "state", None)
    def _get_city(self, obj):
        profile = self._get_profile(obj)
        return getattr(profile, "city", None)
    def _get_zip_code(self, obj):
        profile = self._get_profile(obj)
        return getattr(profile, "zip_code", None)

class ArtistMetricsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    uri = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    date_joined = serializers.ReadOnlyField()
    user_id = serializers.SerializerMethodField('get_user_id', read_only=True)
    campaign = serializers.SerializerMethodField('get_campaign_id', read_only=True)

    # from artist profile
    country = serializers.SerializerMethodField('_get_country', read_only=True)
    state = serializers.SerializerMethodField('_get_state', read_only=True)
    city = serializers.SerializerMethodField('_get_city', read_only=True)
    zip_code = serializers.SerializerMethodField('_get_zip_code', read_only=True)

    class Meta:
        model = cnt_models.Artist
        fields = [
            'id',
            'uri',
            'name',
            'date_joined',
            'user_id',
            'campaign',
            'country',
            'state',
            'city',
            'zip_code',
        ]
    
    def _get_profile(self, obj):
        user = getattr(obj, 'artist_user', None)
        if user == None:
            return None
        profile = getattr(user, 'profile', None)
        if profile == None:
            return None
        return profile

    def get_user_id(self, obj):
        if hasattr(obj, 'artist_user'):
            return obj.artist_user.id
        else:
            return None
    
    def get_campaign_id(self, obj):
        profile = self._get_profile(obj)
        if profile == None:
            return None
        campaign = getattr(profile, 'campaign', None)
        if campaign == None:
            return None
        return getattr(campaign, 'id', None)
    
    def _get_artist_profile(self, obj):
        return getattr(obj, "artist_profile", None)
    
    def _get_country(self, obj):
        artist_profile = self._get_artist_profile(obj)
        country = getattr(artist_profile, "country", None)
        return country
    def _get_state(self, obj):
        artist_profile = self._get_artist_profile(obj)
        state = getattr(artist_profile, "state", None)
        return state
    def _get_city(self, obj):
        artist_profile = self._get_artist_profile(obj)
        city = getattr(artist_profile, "city", None)
        return city
    def _get_zip_code(self, obj):
        artist_profile = self._get_artist_profile(obj)
        code = getattr(artist_profile, "zip_code", None)
        return code


class AlbumMetricsSerializer(serializers.ModelSerializer):

    artist_id = serializers.SerializerMethodField('get_artist_id', read_only=True)

    class Meta:
        model = cnt_models.Album
        fields = [
            'id',
            'uri',
            'name',
            'type',
            'uploaded_date',
            'last_changed',
            'date_published',
            'is_displayed',
            'is_deleted',
            'artist_id',
        ]
    
    def get_artist_id(self, obj):
        if hasattr(obj, 'uploaded_by') and (obj.uploaded_by != None):
            return obj.uploaded_by.id
        else:
            return None


class SongMetricsSerializer(serializers.ModelSerializer):

    album_id = serializers.ReadOnlyField(source='album.id')
    artist_id = serializers.ReadOnlyField(source='uploaded_by.id')

    class Meta:
        model = cnt_models.Song
        fields = [
            'id',
            'uri',
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


class ContactFormMetricsSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')
    name = serializers.SerializerMethodField('get_name', read_only=True)

    class Meta:
        model = ContactForm
        fields = [
            'id',
            'user_id',
            'name',
            'email',
            'subject',
            'message',
            'resolved',
            'assigned_to',
        ]

    def get_name(self, obj):
        string = obj.first_name if obj.first_name != None else None
        if obj.last_name != None:
            string += " {}".format(obj.last_name)
        return string


class CampaignMetricsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Campaign
        fields = [
            'id',
            'uri',
            'name',
            'budget',
            'spent',
            'destination',
        ]


class StreamMetricsSerializer(serializers.ModelSerializer):

    song_id = serializers.ReadOnlyField(source='song.id')
    user_id = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Stream
        fields = [
            'id',
            'song_id',
            'user_id',
            'alternate_platform',
            'timestamp',
            'stream_duration',
            'is_downloaded',
            'is_saved',
            'source',
        ]


