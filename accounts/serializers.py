from knox.models import AuthToken
from .models import *
from music.models import Artist
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.forms.models import model_to_dict

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['country','image']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username','email','profile']
    
    # TODO: overwrite request methods (create, list)
    # we have no idea what method accouts/profile is calling, not list or retrieve

class CreateAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username','email','password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(validated_data['username'],
                                            validated_data['email'],
                                            validated_data['password'])
        return user

class LoginAccountSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in, please try again")

class UserArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'
