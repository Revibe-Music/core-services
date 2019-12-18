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
        elif raise_exception:
            key = next(iter(self.errors))
            value = self.errors[key]
            raise Exception("Invalid data: {} - {}".format(key, value))


    def validate_data(self, *args, **kwargs):
        for key in self.data.keys():
            if key not in self.Meta.fields:
                self.errors.update({key: "unknown field: {}".format(key)})
        for field in self.Meta.fields:
            if field not in self.data.keys():
                self.errors.update({field: "field '{}' must be included in data".format(field)})

    def save(self, *args, **kwargs):
        assert self.validated, "Must call is_valid"

        instance = self.create(**self.data)
        if not isinstance(instance, self.Meta.model):
            raise ValueError("Could not create row")
    
    def create(self, **validated_data):
        instance = self.Meta.model(**validated_data) # don't think this will work but we'll find out
        instance.save()
        return instance

class StreamSerializer(DynamoDBSerializer):
    class Meta:
        model = Stream
        fields = [
            'song',
            'user',
            'stream_duration',
            'is_downloaded',
            'is_saved',
            'device',
        ]

