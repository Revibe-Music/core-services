from allauth.socialaccount.models import SocialToken, SocialApp
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.files.images import get_image_dimensions
from django.forms.models import model_to_dict
from django.utils import timezone
from oauth2_provider.models import AccessToken, RefreshToken
from oauth2_provider.generators import generate_client_id
from rest_framework import serializers

from revibe._helpers.files import add_image_to_obj

from accounts.models import *
from content.models import Artist, Image
from content.serializers.v1 import ImageSerializer
from music.models import Library

# -----------------------------------------------------------------------------

class SocialMediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = SocialMedia
        fields = [
            '_get_service',
            'handle',
        ]


class ProfileSerializer(serializers.ModelSerializer): # TODO: do this right, please
    allow_explicit = serializers.BooleanField(required=False)
    allow_listening_data = serializers.BooleanField(required=False)
    allow_email_marketing = serializers.BooleanField(required=False)
    skip_youtube_when_phone_is_locked = serializers.BooleanField(required=False)
    class Meta:
        model = Profile
        fields = [
            'email',
            'country',
            'image',
            'allow_explicit',
            'allow_listening_data',
            'allow_email_marketing',
            'skip_youtube_when_phone_is_locked',
        ]


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    profile = ProfileSerializer(many=False, required=False)


    device_id = serializers.CharField(required=False)
    device_type = serializers.CharField(required=False)
    device_name = serializers.CharField(required=False)

    # read-only
    user_id = serializers.ReadOnlyField(source='id')
    is_artist = serializers.BooleanField(read_only=True)
    is_manager = serializers.BooleanField(read_only=True)

    # write-only
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'user_id',
            'first_name',
            'last_name',
            'username',
            'profile',


            'device_id',
            'device_type',
            'device_name',

            # read-only
            'is_artist',
            'is_manager',

            # write-only
            'password',
        ]

    def create(self, validated_data):
        remove = ['device_type',]
        data = {}
        for key, value in validated_data.items():
            if key not in remove:
                data.update({key: value})
        validated_data = data
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        profile = Profile.objects.create(user=user, **profile_data)
        profile.save()
        for plat in ['Revibe', 'YouTube']:
            library = Library.objects.create(user=user, platform=plat)
            library.save()
        return user
    
    def update(self, instance, validated_data, *args, **kwargs):

        profile_data = validated_data.pop('profile', False)
        if profile_data:
            profile = Profile.objects.filter(user=instance).update(**profile_data)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance


class UserPatchSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False, required=False)
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'profile'
        ]
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'username': {'required': False},
            'email': {'required': False},
        }


class LoginAccountSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    device_id = serializers.CharField(required=False)
    device_type = serializers.CharField(required=False)
    device_name = serializers.CharField(required=False)

    def validate(self, data):
        data = {"username": data['username'], "password": data['password']}
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in, please try again")


class AccessTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class UserArtistProfileSerializer(serializers.ModelSerializer):
    about_me = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    zip_code = serializers.CharField(required=False)

    require_contribution_approval = serializers.BooleanField(required=False)
    require_contribution_approval_on_edit = serializers.BooleanField(required=False)
    share_data_with_contributors = serializers.BooleanField(required=False)
    share_advanced_data_with_contributors = serializers.BooleanField(required=False)
    allow_contributors_to_edit_contributions = serializers.BooleanField(required=False)
    display_other_platform_content_on_revibe_page = serializers.BooleanField(required=False)

    # read-only
    profile_id = serializers.ReadOnlyField(source='id')
    social_media = SocialMediaSerializer(read_only=True, many=True)

    class Meta:
        model = ArtistProfile
        fields = [
            'profile_id',

            # profile fields
            'about_me',
            'email',
            'country',
            'state',
            'city',
            'zip_code',

            # settings fields
            'require_contribution_approval',
            'require_contribution_approval_on_edit',
            'share_data_with_contributors',
            'share_advanced_data_with_contributors',
            'allow_contributors_to_edit_contributions',
            'display_other_platform_content_on_revibe_page',

            # social media
            'social_media',
        ]


class UserArtistSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    platform = serializers.CharField(required=False)

    # read only
    artist_id = serializers.ReadOnlyField(source='id')
    artist_uri = serializers.ReadOnlyField(source='uri')
    artist_profile = UserArtistProfileSerializer(read_only=True)
    user = UserSerializer(source='artist_user', read_only=True)
    images = ImageSerializer(source='artist_image', many=True, read_only=True)

    # write only
    image = serializers.FileField(write_only=True, allow_null=True, required=False)

    about_me = serializers.CharField(source="artist_profile.about_me", required=False, write_only=True)
    email = serializers.CharField(source="artist_profile.email", required=False, write_only=True)
    country = serializers.CharField(source="artist_profile.country", required=False, write_only=True)
    state = serializers.CharField(source="artist_profile.state", required=False, write_only=True)
    city = serializers.CharField(source="artist_profile.city", required=False, write_only=True)
    zip_code = serializers.CharField(source="artist_profile.zip_code", required=False, write_only=True)

    require_contribution_approval = serializers.BooleanField(source="artist_profile.require_contribution_approval", write_only=True)
    require_contribution_approval_on_edit = serializers.BooleanField(source="artist_profile.require_contribution_approval_on_edit", write_only=True)
    share_data_with_contributors = serializers.BooleanField(source="artist_profile.share_data_with_contributors", write_only=True)
    share_advanced_data_with_contributors = serializers.BooleanField(source="artist_profile.share_advanced_data_with_contributors", write_only=True)
    allow_contributors_to_edit_contributions = serializers.BooleanField(source="artist_profile.allow_contributors_to_edit_contributions", write_only=True)
    display_other_platform_content_on_revibe_page = serializers.BooleanField(source="artist_profile.display_other_platform_content_on_revibe_page", write_only=True)

    class Meta:
        model = Artist
        fields = [
            'name',
            'platform',

            # read-only
            'artist_id',
            'artist_uri',
            'images',
            'artist_profile',
            'user',

            # write only
            'image',

            # profile fields
            'about_me',
            'email',
            'country',
            'state',
            'city',
            'zip_code',

            # profile settings fields
            'require_contribution_approval',
            'require_contribution_approval_on_edit',
            'share_data_with_contributors',
            'share_advanced_data_with_contributors',
            'allow_contributors_to_edit_contributions',
            'display_other_platform_content_on_revibe_page',
        ]
    
    def _get_artist_profile_fields(self):
        fields = [
            'about_me',
            'email',
            'country',
            'city',
            'zip_code',
            'require_contribution_approval',
            'share_data_with_contributors',
            'share_advanced_data_with_contributors',
        ]
        return fields
    
    def create(self, validated_data, *args, **kwargs):
        artist_profile_data = validated_data.pop('artist_profile', False)
        img = validated_data.pop('image', None)

        artist = Artist.objects.create(**validated_data)
        artist.save()

        profile = ArtistProfile.objects.create(artist=artist)
        if 'email' in artist_profile_data.keys():
            profile.email = artist_profile_data['email']
        profile.save()

        image_obj = add_image_to_obj(artist, img)

        return artist
    
    def update(self, instance, validated_data, *args, **kwargs):
        artist_profile_data = validated_data.pop('artist_profile', False)
        img = validated_data.pop('image', None)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        if artist_profile_data:
            artist_profile = instance.artist_profile
            for key, value in artist_profile_data.items():
                setattr(artist_profile, key, value)
            artist_profile.save()

        image_obj = add_image_to_obj(instance, img, edit=True)

        return instance


class SocialTokenSerializer(serializers.ModelSerializer):
    platform = serializers.ReadOnlyField(source='app.name')
    class Meta:
        model = SocialToken
        fields = [
            'platform',
            'token',
            'token_secret',
            'expires_at',
        ]

