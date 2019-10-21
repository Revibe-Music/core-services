from django.contrib.auth.models import User, Group
from .models import *
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url','username','email','groups']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class SongSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Song
        fields = ['song','title','artist','album','duration']

class ArtistSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Artist
        fields = ['name','image']

class AlbumSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Album
        fields = ['name','image','artist']
