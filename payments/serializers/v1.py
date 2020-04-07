"""
Created: 30 Mar. 2020
Author: Jordan Prechac
"""

from django.contrib.auth.models import AnonymousUser
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
        request = self.context.get('request')
        donor = getattr(request, "user", None)
        skip_donor = not (donor == None or isinstance(donor, AnonymousUser))
        if skip_donor and donor.profile.allow_donation_data:
            validated_data['donor'] = donor

        recipient_id = validated_data.pop('recipient', None)
        if recipient_id == None:
            raise network.ExpectationFailedError(detail="No value for 'recipient' found")
        recipient = Artist.objects.get(id=recipient_id)

        donation = ThirdPartyDonation.objects.create(recipient=recipient, **validated_data)

        return donation


