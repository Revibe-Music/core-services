from .models import *
from music.models import Artist, Library
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.forms.models import model_to_dict
from allauth.socialaccount.models import SocialToken
from oauth2_provider.models import AccessToken, RefreshToken
from oauth2_provider.generators import generate_client_id
from django.conf import settings
from django.utils import timezone


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['country','image']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'password','email','profile']
        extra_kwargs = {'password': {'write_only': True}, 'profile': {'required': False}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = CustomUser.objects.create_user(**validated_data)
        user.save()
        profile = Profile.objects.create(user=user, **profile_data)
        profile.save()
        for plat in ['Revibe', 'YouTube']:
            library = Library.objects.create(user=user, platform=palt)
            library.save()
        return user

    def update(self, instance, validated_data):
        # TODO: fix this
        profile_data = validated_data.pop('profile')
        profile = instance.profile

        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        # for all fields in profile
        # profile.field = profile_data.get(
        #   'field',
        #   profile.field
        # )
        profile.save()

        return instance

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

class UserArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'

class SocialTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialToken
        fields = ['token', 'token_secret', 'expires_at']
