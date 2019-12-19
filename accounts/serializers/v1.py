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
    class Meta:
        model = Profile
        fields = ['country','image']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False, required=False)
    device_id = serializers.CharField(required=False)
    device_type = serializers.CharField(required=False)
    device_name = serializers.CharField(required=False)
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
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
        extra_kwargs = {
            'password': {'write_only': True},
            'is_artist': {'read_only': True},
            'is_manager': {'read_only': True},
        }

    def create(self, validated_data):
        remove = ['device_id', 'device_name','device_type']
        for a in remove:
            del validated_data[a]
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
    image_up = serializers.FileField(source='image', write_only=True, allow_null=True, required=False)
    class Meta:
        model = Artist
        fields = [
            'name',
            'platform',

            # read-only
            'artist_id',
            'artist_uri',
            'user',
            'artist_profile',

            # write only
            'image_up',
        ]
    
    def create(self, validated_data, *args, **kwargs):
        # request = self.context.get("request")
        # user = request.user
        # if not user:
        #     raise Exception("Could not identify user")

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
