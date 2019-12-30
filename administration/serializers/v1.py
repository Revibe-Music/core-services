from rest_framework import serializers

import logging
logger = logging.getLogger(__name__)

from accounts import models as acc_models
from accounts.serializers.v1 import UserSerializer
from administration.models import *

# ------

class ContactFormSerializer(serializers.ModelSerializer):

    subject = serializers.CharField(required=True)
    message = serializers.CharField(required=True)

    # read-only
    id = serializers.IntegerField(read_only=True)
    user = UserSerializer(read_only=True)
    resolved = serializers.BooleanField(read_only=True)
    assigned_to = serializers.BooleanField(read_only=True)

    # write-only
    user_id = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = ContactForm
        fields = [
            'subject',
            'message',

            # read-only
            'id',
            'user',
            'resolved',
            'assigned_to',

            # write-only
            'user_id'
        ]


class UserMetricsSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    last_login = serializers.ReadOnlyField()
    is_staff = serializers.ReadOnlyField()

    class Meta:
        model = acc_models.CustomUser
        fields = [
            'username',
            'first_name',
            'last_name',
            'last_login',
            'is_staff',
            'date_joined',
        ]
