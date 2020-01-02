from django.shortcuts import get_object_or_404
from rest_framework import serializers

from content.models import *
from content.mixins import ContributionSerializerMixin


# class ImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Image
#         fields = '__all__'


class ArtistSerializer(serializers.ModelSerializer):
    artist_id = serializers.CharField(source='id', required=False)
    artist_uri = serializers.CharField(source='uri', required=False)
    name = serializers.CharField(required=True)
    platform = serializers.CharField(required=True)

    # read-only
    ext = serializers.SerializerMethodField('image_extension', read_only=True)

    # write-only
    image = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Artist
        fields = [
            'artist_id',
            'artist_uri',
            'name',
            'platform',

            # read-only
            'ext',

            # write-only
            'image',
        ]
    
    def image_extension(self, obj):
        if hasattr(obj, 'image') and obj.image != None:
            return obj.image.name.split('.')[-1]
        else:
            return None


class SongContributorSerializer(serializers.ModelSerializer, ContributionSerializerMixin):
    artist_id = serializers.CharField(source='artist.id', required=False)
    song_id = serializers.CharField(source='song.id', required=False)
    contribution_type = serializers.CharField(required=False)
    approved = serializers.BooleanField(required=False)
    pending = serializers.BooleanField(required=False)

    # read-only
    contribution_id = serializers.ReadOnlyField(source='id')
    artist_name = serializers.ReadOnlyField(source='artist.name')
    artist_uri = serializers.ReadOnlyField(source='artist.uri')
    song_title = serializers.ReadOnlyField(source='song.title')
    song_uri = serializers.ReadOnlyField(source='song.uri')

    class Meta:
        model = SongContributor
        fields = [
            'artist_id',
            'song_id',
            'contribution_type',
            'approved',
            'pending',

            # read-only
            'contribution_id',
            'artist_name',
            'artist_uri',
            'song_title',
            'song_uri',
        ]
    
    def create(self, validated_data):
        artist = Artist.objects.filter(platform='Revibe').get(pk=validated_data.pop('artist_id'))
        song = Song.objects.filter(platform='Revibe').get(pk=validated_data.pop('song_id'))

        song_contrib = SongContributor(**validated_data, artist=artist, song=song)

        # change contribution based on account settings
        artist_settings = self.get_account_settings(artist)
        if artist_settings:
            song_contrib.pending = artist_settings['pending']
            song_contrib.approved = artist_settings['approved']

        song_contrib.save()

        return song_contrib


class AlbumContributorSerializer(serializers.ModelSerializer, ContributionSerializerMixin):
    artist_id = serializers.CharField(source='artist.id', required=False)
    album_id = serializers.CharField(source='album.id', required=False)
    contribution_type = serializers.CharField(required=True)
    approved = serializers.BooleanField(required=False, default=True)
    pending = serializers.BooleanField(required=False, default=False)

    # read-only
    contribution_id = serializers.ReadOnlyField(source='id')
    artist_name = serializers.ReadOnlyField(source='artist.name')
    artist_uri = serializers.ReadOnlyField(source='artist.uri')
    album_name = serializers.ReadOnlyField(source='album.name')
    album_uri = serializers.ReadOnlyField(source='album.uri')

    class Meta:
        model = AlbumContributor
        fields = [
            'artist_id',
            'album_id',
            'contribution_type',
            'approved',
            'pending',

            # read-only
            'contribution_id',
            'artist_name',
            'artist_uri',
            'album_name',
            'album_uri',
        ]
    
    def create(self, validated_data):
        artist = Artist.objects.filter(platform='Revibe').get(pk=validated_data.pop('artist_id'))
        album = Album.objects.filter(platform='Revibe').get(pk=validated_data.pop('album_id'))

        album_contributor = AlbumContributor(**validated_data, artist=artist, album=album)

        artist_settings = self.get_account_settings(artist)
        if artist_settings:
            album_contributor.pending = artist_settings['pending']
            album_contributor.approved = artist_settings['approved']

        album_contributor.save()
        
        return album_contributor


class AlbumSerializer(serializers.ModelSerializer):
    album_id = serializers.CharField(source='id', required=False)
    album_uri = serializers.CharField(source='uri', required=False)
    name = serializers.CharField(required=False)
    type = serializers.CharField(required=False)
    platform = serializers.CharField(required=False)
    is_displayed = serializers.BooleanField(required=False, default=True)

    # read-only
    ext = serializers.SerializerMethodField('get_ext', read_only=True)
    artist = ArtistSerializer(source='album_uploaded_by', read_only=True)
    contributors = AlbumContributorSerializer(source='album_to_artist', many=True, read_only=True)
    uploaded_date = serializers.DateField(read_only=True)
    last_changed = serializers.DateField(read_only=True)

    # write-only
    image = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Album
        fields = [
            'album_id',
            'album_uri',
            'name',
            'type',
            'platform',
            'is_displayed',

            # read-only
            'ext',
            'artist',
            'contributors',
            'uploaded_date',
            'last_changed',

            # write-only
            'image',
        ]

    def create(self, validated_data):
        artist = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            artist = request.user.artist
        else:
            raise Exception("problem") # implement custom exception class

        album = Album(**validated_data, uploaded_by=artist)
        album.save()

        album_contrib = AlbumContributor.objects.create(artist=artist, album=album, contribution_type="Artist", primary_artist=True)
        album_contrib.save()

        return album

    def get_ext(self, obj):
        if hasattr(obj, "image") and (obj.image != None):
            return obj.image.name.split('.')[-1]
        else:
            return None


class SongSerializer(serializers.ModelSerializer):
    song_id = serializers.CharField(source='id', required=False)
    song_uri = serializers.CharField(source='uri', required=False)
    genre = serializers.CharField(required=False)
    is_explicit = serializers.BooleanField(required=False, default=False)
    is_displayed = serializers.BooleanField(required=False, default=True)

    # read-only
    artist = ArtistSerializer(source='song_uploaded_by', read_only=True)
    album = AlbumSerializer(read_only=True)
    contributors = SongContributorSerializer(source='song_to_artist', many=True, read_only=True)
    uploaded_date = serializers.DateField(read_only=True)
    last_changed = serializers.DateField(read_only=True)

    # write-only
    album_id = serializers.CharField(write_only=True, required=True)
    file = serializers.FileField(write_only=True, required=True)

    class Meta:
        model = Song
        fields = [
            'song_id',
            'song_uri',
            'title',
            'duration',
            'genre',
            'platform',
            'is_explicit',
            'is_displayed',

            # read-only
            'album',
            'artist',
            'contributors',
            'uploaded_date',
            'last_changed',

            # write-only
            'album_id',
            'file',
        ]
    
    def create(self, validated_data):
        album = Album.objects.get(pk=validated_data.pop('album_id'))

        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            artist = request.user.artist
        else:
            raise Exception("some issue") # TODO: custom exception later

        song = Song(**validated_data, uploaded_by=artist, album=album)
        song.save()

        song_contrib = SongContributor(artist=artist, song=song, contribution_type="Artist", primary_artist=True)
        song_contrib.save()

        return song


# Non-Revibe Content Serializers

class OtherArtistSerializer(serializers.ModelSerializer):
    artist_id = serializers.CharField(source='id', required=False)
    artist_uri = serializers.CharField(source='uri', required=False)

    class Meta:
        model = Artist
        fields = [
            'artist_id',
            'artist_uri',
            'name',
            'image',
            'platform',
        ]


class OtherAlbumSerializer(serializers.ModelSerializer):
    album_id = serializers.CharField(source='id', required=False)
    artist_uri = serializers.CharField(source='uri', required=False)
    uploaded_by = OtherArtistSerializer(read_only=True)

    class Meta:
        model = Album
        fields = [
            'album_id',
            'album_uri',
            'name',
            'type',
            'image_ref',
            'platform',
            'uploaded_by',
        ]


class OtherSongSerializer(serializers.ModelSerializer):
    song_id = serializers.CharField(source='id', required=False)
    song_uri = serializers.CharField(source='uri', required=False)
    album = OtherAlbumSerializer(read_only=True)
    uploaded_by = OtherArtistSerializer(read_only=True)

    class Meta:
        model = Song
        fields = [
            'song_id',
            'song_uri',
            'title',
            'duration',
            'genre',
            'platform',
            'is_explicit',
            'album',
            'uploaded_by',
        ]

