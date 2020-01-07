from allauth.socialaccount.models import SocialToken, SocialApp
from django.conf import settings
from django.contrib.auth import authenticate
from django.forms.models import model_to_dict
from django.utils import timezone
from oauth2_provider.models import AccessToken, RefreshToken
from oauth2_provider.generators import generate_client_id
from rest_framework import serializers

from accounts.models import *
from content.models import Artist
from music.models import Library

class ProfileSerializer(serializers.ModelSerializer): # TODO: do this right, please
    allow_explicit = serializers.BooleanField(required=False)
    allow_listening_data = serializers.BooleanField(required=False)
    allow_email_marketing = serializers.BooleanField(required=False)
    class Meta:
        model = Profile
        fields = [
            'email',
            'country',
            'image',
            'allow_explicit',
            'allow_listening_data',
            'allow_email_marketing',
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
    city = serializers.CharField(required=False)
    zip_code = serializers.CharField(required=False)

    require_contribution_approval = serializers.BooleanField(required=False, default=True)
    share_data_with_contributors = serializers.BooleanField(required=False, default=True)
    share_advanced_data_with_contributors = serializers.BooleanField(required=False, default=False)
    allow_contributors_to_edit_contributions = serializers.BooleanField(required=False, default=False)

    # read-only
    profile_id = serializers.ReadOnlyField(source='id')

    class Meta:
        model = ArtistProfile
        fields = [
            'profile_id',

            # profile fields
            'about_me',
            'email',
            'country',
            'city',
            'zip_code',

            # settings fields
            'require_contribution_approval',
            'share_data_with_contributors',
            'share_advanced_data_with_contributors',
            'allow_contributors_to_edit_contributions',
        ]

class UserArtistSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    platform = serializers.CharField(required=False)

    # read only
    artist_id = serializers.ReadOnlyField(source='id')
    artist_uri = serializers.ReadOnlyField(source='uri')
    ext = serializers.SerializerMethodField('image_extension', read_only=True)
    artist_profile = UserArtistProfileSerializer(read_only=True)
    user = UserSerializer(source='artist_user', read_only=True)

    # write only
    image = serializers.FileField(write_only=True, allow_null=True, required=False)

    about_me = serializers.CharField(source="artist_profile.about_me", required=False, write_only=True)
    email = serializers.CharField(source="artist_profile.email", required=False, write_only=True)
    country = serializers.CharField(source="artist_profile.country", required=False, write_only=True)
    city = serializers.CharField(source="artist_profile.city", required=False, write_only=True)
    zip_code = serializers.CharField(source="artist_profile.zip_code", required=False, write_only=True)

    require_contribution_approval = serializers.BooleanField(source="artist_profile.require_contribution_approval", required=False, write_only=True)
    share_data_with_contributors = serializers.BooleanField(source="artist_profile.share_data_with_contributors", required=False, write_only=True)
    share_advanced_data_with_contributors = serializers.BooleanField(source="artist_profile.share_advanced_data_with_contributors", required=False, write_only=True)
    allow_contributors_to_edit_contributions = serializers.BooleanField(source="artist_profile.allow_contributors_to_edit_contributions", required=False, default=False)

    class Meta:
        model = Artist
        fields = [
            'name',
            'platform',

            # read-only
            'artist_id',
            'artist_uri',
            'ext',
            'artist_profile',
            'user',

            # write only
            'image',

            # profile fields
            'about_me',
            'email',
            'country',
            'city',
            'zip_code',

            # profile settings fields
            'require_contribution_approval',
            'share_data_with_contributors',
            'share_advanced_data_with_contributors',
            'allow_contributors_to_edit_contributions',
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

        artist = Artist(**validated_data)
        artist.save()

        if artist_profile_data:
            profile = ArtistProfile(**artist_profile_data, artist=artist)
        else:
            profile = ArtistProfile(artist=artist)
        profile.save()

        return artist
    
    def update(self, instance, validated_data, *args, **kwargs):
        artist_profile_data = validated_data.pop('artist_profile', False)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        if artist_profile_data:
            artist_profile = instance.artist_profile
            for key, value in artist_profile_data.items():
                setattr(artist_profile, key, value)
            artist_profile.save()
        
        return instance

    def image_extension(self, obj):
        if obj.image:
            return obj.image.name.split('.')[-1]
        else:
            return False

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
