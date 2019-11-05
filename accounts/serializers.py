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
        fields = ['first_name', 'last_name', 'username', 'password','email','profile']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = CustomUser.objects.create(**validated_data)
        user.save()
        profile = Profile.objects.create(user=user, **profile_data)
        profile.save()
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

# class CreateAccountSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ['username','email','password']
#         extra_kwargs = {'password': {'write_only': True}}
    
#     def create(self, validated_data):
#         user = CustomUser.objects.create_user(validated_data['username'],
#                                             validated_data['email'],
#                                             validated_data['password'])
#         return user

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
