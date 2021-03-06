"""
"""

from rest_framework import serializers

from revibe.exceptions.api import ServiceUnavailableError

from accounts.models import CustomUser
from accounts.referrals.models import Point, Referral
from accounts.referrals.utils.models.referral import attach_referral

# -----------------------------------------------------------------------------


class ReferralSerializer(serializers.ModelSerializer):
    ip_address = serializers.CharField(source='referree_ip_address', required=False)
    user_id = serializers.CharField(source='referrer.id')

    class Meta:
        model = Referral
        fields = [
            'id',
            'user_id', # ID of the referring user
            'ip_address',
        ]
        read_only_fields = [
            'id',
        ]

    def create(self, validated_data, *args, **kwargs):
        user = None
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            user  = request.user
        else:
            raise serializers.ValidationError("Could not identify the request user")

        referrer_id = validated_data.pop('referrer')['id']
        referrer = CustomUser.objects.get(id=referrer_id)

        # create referral
        instance = attach_referral(referrer=referrer, referree=user, **validated_data)

        return instance


    def update(self, instance, validated_data, *args, **kwargs):
        raise ServiceUnavailableError("Cannot edit referrals")


class PointSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField('_get_category_name', read_only=True)

    class Meta:
        model = Point
        fields = [
            'id',
            'category_name',
            'points',
            'timestamp',
        ]

    def create(self, validated_data, *args, **kwargs):
        pass
    def create(self, instance, validated_data, *args, **kwargs):
        pass

    def _get_category_name(self, obj):
        if obj.category:
            return obj.category.name
        return None



