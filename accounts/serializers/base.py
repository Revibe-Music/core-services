"""
Created: 31 Mar. 2020
Author: Jordan Prechac
"""

from rest_framework import serializers

from revibe._errors.data import ObjectAlreadyExists

from ..models import SocialMedia

# -----------------------------------------------------------------------------


class BaseSocialMediaSerializer(serializers.ModelSerializer):

    order = serializers.IntegerField(required=False)

    # read-only
    id = serializers.ReadOnlyField()
    social_media = serializers.CharField(source='_get_service', read_only=True)

    # write-only
    description = serializers.CharField(write_only=True, required=False)
    service = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = SocialMedia
        fields = [
            'id', # read-only
            'social_media', # read-only
            'handle',
            'order',

            # write-only
            'description',
            'service',
        ]

    def create(self, validated_data):
        # get artist profile
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            artist_profile = request.user.artist.artist_profile

        # check that this artist doesn't already have a social media with this service
        if validated_data['service'] != 'other':
            medias = SocialMedia.objects.filter(artist_profile=artist_profile, service=validated_data['service'])
            if len(medias) > 0:
                raise ObjectAlreadyExists()

        validated_data['artist_profile'] = artist_profile
        return super().create(validated_data)