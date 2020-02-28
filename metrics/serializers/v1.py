from django.conf import settings
from rest_framework import serializers

from revibe._errors import network

from accounts.models import CustomUser
from content.models import Song
from metrics.models import *

# -----------------------------------------------------------------------------


class StreamSerializer(serializers.ModelSerializer):

    # write-only
    song_id = serializers.CharField(write_only=True)
    user_id = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Stream
        fields = [
            'stream_duration',
            'is_downloaded',
            'is_saved',
            'song_id',
            'user_id',
        ]
    
    def create(self, validate_data):
        song_id = validate_data.pop('song_id')
        try:
            song = Song.objects.get(id=song_id)
        except Song.DoesNotExist as e:
            raise network.BadEnvironmentError("This song_id has not yet been recorded, this is normal for non-Revibe content.")

        stream = Stream.objects.create(**validate_data, song=song)

        user = self.context.get("request").user
        if user and user.profile.allow_listening_data:
            stream.user = user

        stream.save()

        return stream


# -----------------------------------------------------------------------------
# DEPRECATED
# Used to use AWS DynamoDB for tracking stream information

# class DynamoDBSerializer:
#     def __init__(self, data=None, *args, **kwargs):
#         if data == None:
#             raise ValueError("Must include data when instantiating {}".format(self.__class__.__name__))
#         assert hasattr(self, "Meta"), "Must implement a Meta class in a DynamoDBSerializer"
#         assert hasattr(self.Meta, "model"), "Must implement a 'model' a DynamoDBSerializer.Meta"
#         self.data=data
#         self.validated = False
#         self.errors = {}

#     def is_valid(self, raise_exception=False):
#         self.validate_data()
#         if len(self.errors) == 0:
#             self.validated = True
#             return True
#         elif raise_exception:
#             key = next(iter(self.errors))
#             value = self.errors[key]
#             raise Exception("Invalid data: {} - {}".format(key, value))
#         return False


#     def validate_data(self, *args, **kwargs):
#         for key in self.data.keys():
#             if key not in self.Meta.fields:
#                 self.errors.update({key: "unknown field: {}".format(key)})
#         for field in self.Meta.fields:
#             if field not in self.data.keys():
#                 self.errors.update({field: "field '{}' must be included in data".format(field)})

#     def save(self, *args, **kwargs):
#         assert self.validated, "Must call is_valid"

#         instance = self.create(self.data, *args, **kwargs)
#         if not isinstance(instance, self.Meta.model):
#             raise ValueError("Could not create row")
#         self.instance = instance
#         return instance
    
#     def create(self, **validated_data):
#         # instance = self.Meta.model(**validated_data) # don't think this will work but we'll find out
#         # instance.save()
#         # return instance
#         raise NotImplementedError("must implement '{}.create()'".format(self.__class__.__name__))

# class StreamSerializer(DynamoDBSerializer):
#     class Meta:
#         model = Stream
#         fields = [
#             'song_id',
#             'user_id',
#             'stream_duration',
#             'is_downloaded',
#             'is_saved',
#             'device',
#         ]

#     def create(self, validated_data, *args, **kwargs):
#         environment = "test" if settings.DEBUG else "production"

#         stream = self.Meta.model(
#             song_id = validated_data['song_id'],
#             user_id = validated_data['user_id'] if validated_data['user_id'] else 'opt-out',
#             stream_duration = int(validated_data['stream_duration']),
#             stream_percentage = validated_data['stream_percentage'],
#             is_downloaded = validated_data['is_downloaded'],
#             is_saved = validated_data['is_saved'],
#             device = validated_data['device'],
#             environment = environment
#         )
#         stream.save()

#         return stream
