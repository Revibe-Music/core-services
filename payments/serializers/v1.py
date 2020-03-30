"""
Created: 30 Mar. 2020
Author: Jordan Prechac
"""

from rest_framework import serializers

from revibe._errors import network

from ..models import ThirdPartyDonation

from content.models import Artist

# -----------------------------------------------------------------------------


class ThirdPartyDonationSerializer(serializers.ModelSerializer):

    recipient = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = ThirdPartyDonation
        fields = [
            'service',
            'amount',
            'other',

            # write-only
            'recipient',
        ]

    def create(self, validated_data, *args, **kwargs):
        donor = self.context.get('request').user
        if donor.profile.allow_donation_data:
            validated_data['donor'] = donor

        recipient_id = validated_data.pop('recipient', None)
        if recipient_id == None:
            raise network.ExpectationFailedError(detail="No value for 'recipient' found")
        recipient = Artist.objects.get(id=recipient_id)

        donation = ThirdPartyDonation.objects.create(recipient=recipient, **validated_data)

        return donation


