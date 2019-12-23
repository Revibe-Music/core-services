from content.models import Song
from metrics.models import *


class DynamoDBSerializer:
    def __init__(self, data=None, *args, **kwargs):
        if data == None:
            raise ValueError("Must include data when instantiating {}".format(self.__class__.__name__))
        assert hasattr(self, "Meta"), "Must implement a Meta class in a DynamoDBSerializer"
        assert hasattr(self.Meta, "model"), "Must implement a 'model' a DynamoDBSerializer.Meta"
        self.data=data
        self.validated = False
        self.errors = {}

    def is_valid(self, raise_exception=False):
        self.validate_data()
        if len(self.errors) == 0:
            self.validated = True
            return True
        elif raise_exception:
            key = next(iter(self.errors))
            value = self.errors[key]
            raise Exception("Invalid data: {} - {}".format(key, value))
        return False


    def validate_data(self, *args, **kwargs):
        for key in self.data.keys():
            if key not in self.Meta.fields:
                self.errors.update({key: "unknown field: {}".format(key)})
        for field in self.Meta.fields:
            if field not in self.data.keys():
                self.errors.update({field: "field '{}' must be included in data".format(field)})

    def save(self, *args, **kwargs):
        assert self.validated, "Must call is_valid"

        instance = self.create(self.data, *args, **kwargs)
        if not isinstance(instance, self.Meta.model):
            raise ValueError("Could not create row")
        self.instance = instance
    
    def create(self, **validated_data):
        # instance = self.Meta.model(**validated_data) # don't think this will work but we'll find out
        # instance.save()
        # return instance
        raise NotImplementedError("must implement '{}.create()'".format(self.__class__.__name__))

class StreamSerializer(DynamoDBSerializer):
    class Meta:
        model = Stream
        fields = [
            'song_id',
            'user_id',
            'stream_duration',
            'is_downloaded',
            'is_saved',
            'device',
        ]

    def create(self, validated_data, *args, **kwargs):
        song = Song.objects.get(pk=validated_data['song_id'])
        stream_percentage = int(validated_data['stream_duration']) / int(song.duration)

        stream = self.Meta.model(
            song_id = validated_data['song_id'],
            user_id = validated_data['user_id'],
            stream_duration = int(validated_data['stream_duration']),
            stream_percentage = stream_percentage,
            is_downloaded = validated_data['is_downloaded'],
            is_saved = validated_data['is_saved'],
            device = validated_data['device']
        )
        stream.save()

        return stream
