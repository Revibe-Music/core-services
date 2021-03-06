"""
Created: 03 June 2020
Author: Jordan Prechac
"""

from rest_framework import serializers
from django.core.mail import send_mail
from surveys.models import *

# -----------------------------------------------------------------------------


class ArtistOfTheWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistOfTheWeek
        fields = [
            'id',
            'promotion_ideas',
            'picture',
            'facebook_link',
            'instagram_handle',
            'soundcloud_link',
            'spotify_link',
            'youtube_link',
            'other_link_description_1',
            'other_link_1',
            'other_link_description_2',
            'other_link_2',
            'other_link_description_3',
            'other_link_3',
        ]
        read_only_fields = [
            'id',
        ]

    def create(self, validated_data, *args, **kwargs):
        instance = super().create(validated_data, *args, **kwargs)

        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        if user:
            instance.user = user
            instance.save()

        return instance


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'id',
            'first',
            'last',
            'email',
            'subject',
            'message',
            'date_created'
        ]
        read_only_fields = [
            'id',
        ]
    
    def create(self, validated_data, *args, **kwargs):
        instance = super().create(validated_data, *args, **kwargs)

        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            instance.user = user
            instance.save()
        
        return instance
            
