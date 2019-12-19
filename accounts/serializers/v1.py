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

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['country','image']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'username',
            'password',
            'email',
            'profile',
            'is_artist',
            'is_manager',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'is_artist': {'read_only': True},
            'is_manager': {'read_only': True},
            'profile': {'required': False},
        }

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = CustomUser.objects.create_user(**validated_data)
        user.save()
        profile = Profile.objects.create(user=user, **profile_data)
        profile.save()
        for plat in ['Revibe', 'YouTube']:
            library = Library.objects.create(user=user, platform=plat)
            library.save()
        return user
    
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

    def validate(self, data):
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
    require_contribution_approval = serializers.BooleanField(required=False)

    # read-only
    profile_id = serializers.ReadOnlyField(source='id')
    class Meta:
        model = ArtistProfile
        fields = [
            'profile_id',

            # profile fields
            'about_me',

            # settings fields
            'require_contribution_approval',
        ]

class UserArtistSerializer(serializers.ModelSerializer):
    # read only
    artist_id = serializers.ReadOnlyField(source='id')
    artist_uri = serializers.ReadOnlyField(source='uri')
    user = UserSerializer(source='artist_user', read_only=True)
    artist_profile = UserArtistProfileSerializer(read_only=True)

    # write only
    user_id = serializers.UUIDField(write_only=True, required=False)
    image_up = serializers.FileField(source='image', write_only=True, allow_null=True, required=False)
    class Meta:
        model = Artist
        fields = [
            'artist_id',
            'artist_uri',
            'name',
            'platform',
            'user',
            'artist_profile',
            # write only fields
            'user_id',
            'image_up',
        ]
    
    def create(self, validated_data):
        artist = Artist.objects.create(**validated_data)
        artist.save()

        profile = ArtistProfile.objects.create(artist=artist)
        profile.save()

        return artist

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
