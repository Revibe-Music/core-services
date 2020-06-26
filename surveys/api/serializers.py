"""
Created: 03 June 2020
Author: Jordan Prechac
"""

from rest_framework import serializers

from surveys.models import *

# -----------------------------------------------------------------------------


class BaseArtistOfTheWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistOfTheWeek
        fields = [
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


class BaseContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'first',
            'last',
            'email',
            'subject',
            'message',
            'date_created',
        ]

