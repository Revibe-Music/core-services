from django.core.files.images import get_image_dimensions
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from revibe._errors.network import ProgramError
from revibe._helpers.files import add_image_to_obj, add_track_to_song
from revibe.serializers import CustomDateField

from content.models import *
from content.mixins import ContributionSerializerMixin

# -----------------------------------------------------------------------------

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = [
            'url',
            'height',
            'width',
            'is_original',
        ]


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = [
            'url',
            'is_original',
        ]


class ArtistSerializer(serializers.ModelSerializer):
    artist_id = serializers.CharField(source='id', required=False)
    artist_uri = serializers.CharField(source='uri', required=False)
    name = serializers.CharField(required=True)
    platform = serializers.CharField(required=True)

    # read-only
    images = ImageSerializer(source="artist_image", many=True, read_only=True)
    bio = serializers.SerializerMethodField('_get_artist_bio', read_only=True)

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
            'images',
            "bio",

            # write-only
            'image',
        ]
    
    def create(self, validated_data, *args, **kwargs):
        img = validated_data.pop('image', None)

        instance = super().create(validated_data, *args, **kwargs)

        image_obj = add_image_to_obj(instance, img)

        return image_obj
    
    def update(self, instance, validated_data, *args, **kwargs):
        img = validated_data.pop('image', None)

        instance = super().update(instance, validated_data, *args, **kwargs)

        image_obj = add_image_to_object(instance, img, edit=True)

        return instance
    
    def _get_artist_bio(self, obj):
        try:
            profile = getattr(obj, "artist_profile", None)

            if profile == None:
                return None
            
            bio = getattr(profile, "about_me", None)
            return bio
        except Exception:
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
    artist_images = ImageSerializer(source="artist.artist_image", many=True, read_only=True)
    song_tracks = TrackSerializer(source="song.tracks", many=True, read_only=True)

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
            'artist_images',
            'song_tracks',
        ]
    
    def create(self, validated_data):
        artist = validated_data.pop('artist')
        song = validated_data.pop('song')
        artist = Artist.objects.filter(platform='Revibe').get(pk=artist['id'])
        song = Song.objects.filter(platform='Revibe').get(pk=song['id'])

        song_contrib = SongContributor(**validated_data, artist=artist, song=song)

        # change contribution based on account settings
        artist_settings = self.get_account_settings(artist, create=True)
        song_contrib.pending = artist_settings['pending']
        song_contrib.approved = artist_settings['approved']

        song_contrib.save()

        return song_contrib
    
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if not hasattr(instance, 'artist'):
            raise ProgramError("Could not find the artist of this contribution")
        
        artist = instance.artist
        artist_settings = self.get_account_settings(artist, update=True)
        instance.pending = artist_settings['pending']
        instance.approved = artist_settings['approved']
        instance.save()

        return instance


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
    artist_images = ImageSerializer(source="artist.artist_image", many=True, read_only=True)
    album_images = ImageSerializer(source="album.album_image", many=True, read_only=True)

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
            'artist_images',
            'album_images',
        ]
    
    def create(self, validated_data):
        artist = validated_data.pop('artist')
        album = validated_data.pop('album')
        artist = Artist.objects.filter(platform='Revibe').get(pk=artist['id'])
        album = Album.objects.filter(platform='Revibe').get(pk=album['id'])

        album_contributor = AlbumContributor(**validated_data, artist=artist, album=album)

        artist_settings = self.get_account_settings(artist, create=True)
        album_contributor.pending = artist_settings['pending']
        album_contributor.approved = artist_settings['approved']

        album_contributor.save()

        return album_contributor

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if not hasattr(instance, 'artist'):
            raise ProgramError("Could not find the artist of this contribution")

        artist = instance.artist
        artist_settings = self.get_account_settings(artist, update=True)
        instance.pending = artist_settings['pending']
        instance.approved = artist_settings['approved']
        instance.save()

        return instance


class AlbumSerializer(serializers.ModelSerializer):
    album_id = serializers.CharField(source='id', required=False)
    album_uri = serializers.CharField(source='uri', required=False)
    name = serializers.CharField(required=False)
    type = serializers.CharField(required=False)
    platform = serializers.CharField(required=False)
    is_displayed = serializers.BooleanField(required=False)
    # date_published = serializers.DateField(required=False)
    date_published = CustomDateField(required=False, format="%Y-%m-%d")

    # read-only
    uploaded_by = ArtistSerializer(read_only=True)
    contributors = AlbumContributorSerializer(source='album_to_artist', many=True, read_only=True)
    uploaded_date = serializers.DateField(read_only=True)
    last_changed = serializers.DateField(read_only=True)
    images = ImageSerializer(source="album_image", many=True, read_only=True)

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
            'date_published',

            # read-only
            'uploaded_by',
            'contributors',
            'uploaded_date',
            'last_changed',
            'images',

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

        img = validated_data.pop('image', None)

        album = Album(**validated_data, uploaded_by=artist)
        album.is_displayed = True
        album.save()

        album_contrib = AlbumContributor.objects.create(artist=artist, album=album, contribution_type="Artist", primary_artist=True)
        album_contrib.save()

        image_obj = add_image_to_obj(album, img)

        return album

    def update(self, instance, validated_data, *args, **kwargs):
        img = validated_data.pop('image', None)

        instance = super().update(instance, validated_data, *args, **kwargs)

        image_obj = add_image_to_obj(instance, img, edit=True)

        return instance


class SongSerializer(serializers.ModelSerializer):
    song_id = serializers.CharField(source='id', required=False)
    song_uri = serializers.CharField(source='uri', required=False)
    genre = serializers.CharField(required=False)
    is_explicit = serializers.BooleanField(required=False, default=False)
    is_displayed = serializers.BooleanField(required=False, default=True)

    # read-only
    uploaded_by = ArtistSerializer(read_only=True)
    album = AlbumSerializer(read_only=True)
    contributors = SongContributorSerializer(source='song_to_artist', many=True, read_only=True)
    uploaded_date = serializers.DateField(read_only=True)
    last_changed = serializers.DateField(read_only=True)
    tracks = TrackSerializer(read_only=True, many=True)

    # write-only
    album_id = serializers.CharField(write_only=True, required=False)
    file = serializers.FileField(write_only=True, required=False)

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
            'uploaded_by',
            'contributors',
            'uploaded_date',
            'last_changed',
            'tracks',

            # write-only
            'album_id',
            'file',
        ]
    
    def create(self, validated_data):
        album = Album.objects.get(pk=validated_data.pop('album_id'))
        track = validated_data.pop('file', None)

        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            artist = request.user.artist
        else:
            raise Exception("some issue") # TODO: custom exception later

        song = Song(**validated_data, uploaded_by=artist, album=album)
        song.save()

        song_contrib = SongContributor(artist=artist, song=song, contribution_type="Artist", primary_artist=True)
        song_contrib.save()

        track_obj = add_track_to_song(song, track)

        return song
    
    def update(self, instance, validated_data, *args, **kwargs):
        img = validated_data.pop('file', None)

        instance = super().update(instance, validated_data, *args, **kwargs)

        image_obj = add_track_to_song(instance, img, edit=True)

        return instance


# -----------------------------------------------------------------------------
# Non-Revibe Content Serializers

class OtherArtistSerializer(serializers.ModelSerializer):
    artist_id = serializers.CharField(source='id', required=False)
    artist_uri = serializers.CharField(source='uri', required=False)

    # read-only
    images = ImageSerializer(source='artist_image', many=True, read_only=True)    

    # write-only
    image_refs = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Artist
        fields = [
            'artist_id',
            'artist_uri',
            'name',
            'images',
            'platform',

            # write-only
            'image_refs'
        ]
    
    def create(self, validated_data):
        image_refs = validated_data.pop("image_refs", None)
        artist = super().create(validated_data)

        if image_refs != None:
            for i in image_refs:
                im_obj = Image.objects.create(artist=artist, reference=i["ref"], height=i["height"], width=i["width"], is_original=False)
                im_obj.save()
        
        return artist


class OtherAlbumSerializer(serializers.ModelSerializer):
    album_id = serializers.CharField(source='id', required=False)
    album_uri = serializers.CharField(source='uri', required=False)
    uploaded_by = OtherArtistSerializer(read_only=True)
    images = ImageSerializer(source='album_image', many=True, read_only=True)

    # write-only
    image_refs = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Album
        fields = [
            'album_id',
            'album_uri',
            'name',
            'type',
            'images',
            'platform',
            'uploaded_by',

            # write-only
            "image_refs",
        ]
    
    def create(self, validated_data):
        image_refs = validated_data.pop("image_refs", None)
        album = super().create(validated_data)

        if image_refs != None:
            for i in image_refs:
                im_obj = Image.objects.create(album=album, reference=i["ref"], height=i["height"], width=i["width"], is_original=False)
                im_obj.save()
        
        return album


class OtherSongSerializer(serializers.ModelSerializer):
    song_id = serializers.CharField(source='id', required=False)
    song_uri = serializers.CharField(source='uri', required=False)

    # read-only
    album = OtherAlbumSerializer(read_only=True)
    uploaded_by = OtherArtistSerializer(read_only=True)
    tracks = TrackSerializer(many=True, read_only=True)

    # write-only
    platform = serializers.CharField(write_only=True)
    album_id = serializers.CharField(write_only=True)
    artist_id = serializers.CharField(write_only=True)

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

            # read-only
            'album',
            'uploaded_by',
            'tracks',

            # write-only
            'platform',
            'album_id',
            'artist_id',
        ]
    
    def create(self, validated_data, *args, **kwargs):
        platform = validated_data.pop('platform')
        album = Album.objects.get(id=validated_data.pop('album_id'))
        artist = Artist.objects.get(id=validated_data.pop('artist_id'))

        song = Song.objects.create(album=album, uploaded_by=artist, platform=platform, **validated_data)
        song.save()

        return song
        

