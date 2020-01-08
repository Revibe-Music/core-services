from django.db.models import Q
from rest_framework import views, viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response

from revibe.viewsets import *
from revibe._helpers import const
from revibe._helpers.platforms import get_platform

from accounts.permissions import TokenOrSessionAuthentication
from content.mixins import V1Mixin
from content.models import *
from content.serializers import v1 as ser_v1

# -----------------------------------------------------------------------------


class ArtistViewset(PlatformViewSet):
    platform = 'Revibe'
    serializer_class = ser_v1.ArtistSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]],
    }

    def get_queryset(self):
        return self.platform.Artists

    @action(detail=True, url_name="cnt-artist-albums")
    def albums(self, request, pk=None):
        artist = self.get_object()
        queryset = self.platform.Albums.filter(uploaded_by=artist)
        serializer = ser_v1.AlbumSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_name="cnt-artist-songs")
    def songs(self, request, pk=None):
        artist = self.get_object()
        queryset = self.platform.Songs.filter(uploaded_by=artist)
        serializer = ser_v1.SongSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_name="cnt-artist-album-contributions")
    def album_contributions(self, request, pk=None):
        artist = self.get_object()
        queryset = self.platform.AlbumContributors.filter(artist=artist, primary_artist=False)
        serializer = ser_v1.AlbumContributorSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_name="cnt-artist-song-contributions")
    def song_contributions(self, request, pk=None):
        artist = self.get_object()
        queryset = self.platform.SongContributors.filter(artist=artist, primary_artist=False)
        serializer = ser_v1.SongContributorSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True)
    def top_songs(self, request, pk=None):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


class AlbumViewSet(PlatformViewSet):
    platform = 'Revibe'
    serializer_class = ser_v1.AlbumSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"], ['first-party']],
    }

    def get_queryset(self):
        return self.platform.Albums
    
    @action(detail=True)
    def songs(self, request, pk=None, url_name="album-songs"):
        album = self.get_object()
        queryset = self.platform.Songs.filter(album=album)
        serializer = ser_v1.SongSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SongViewSet(PlatformViewSet):
    platform = 'Revibe'
    serializer_class = ser_v1.SongSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]],
    }

    def get_queryset(self):
        return self.platform.Songs


class MusicSearch(GenericPlatformViewSet):
    platform = 'Revibe'
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]],
    }

    def list(self, request, *args, **kwargs):
        params = request.query_params

        if 'text' not in params.keys():
            return Response({"error": "'text' must be included as a parameter in this request"}, status=status.HTTP_417_EXPECTATION_FAILED)
        text = params['text']
        
        result = {}

        t = params.get('type', False)
        if t:
            if t not in ['songs','albums','artists']:
                return Response({'error': "parameter 'type' must be 'songs', 'albums', or 'artists'."}, status=status.HTTP_417_EXPECTATION_FAILED)

        if (t == 'songs') or (not t):
            result['songs'] = ser_v1.SongSerializer(self.search_songs(text), many=True).data
        if (t == 'albums') or (not t):
            result['albums'] = ser_v1.AlbumSerializer(self.search_albums(text), many=True).data
        if (t == 'artists') or (not t):
            result['artists'] = ser_v1.ArtistSerializer(self.search_artists(text), many=True).data

        return Response(result ,status=status.HTTP_200_OK)
    
    def search_songs(self, text, *args, **kwargs):
        assert text, "method 'search_songs' requires a search value."
        limit = const.SEARCH_LIMIT

        # song title is exactly search value
        songs = self.platform.Songs.filter(title__iexact=text).distinct()
        if songs.count() >= limit:
            return songs[:limit]
        
        # artist name is exactly search value
        songs = songs | self.platform.Songs.filter(uploaded_by__name__iexact=text).distinct()
        songs = songs.distinct()
        if songs.count() >= limit:
            return songs[:limit]
        
        # song contributor name is exactly search value
        songs = songs | self.platform.Songs.filter(contributors__name__iexact=text).distinct()
        songs = songs.distinct()
        if songs.count() >= limit:
            return songs[:limit]

        # album name is exactly search value
        songs = songs | self.platform.Songs.filter(album__name__iexact=text).distinct()
        songs = songs.distinct()
        if songs.count() >= limit:
            return songs[:limit]
        
        # title contains search value
        songs = songs | self.platform.Songs.filter(title__icontains=text).distinct()
        songs = songs.distinct()
        if songs.count() >= limit:
            return songs[:limit]
        
        # uploading artist name contains search value
        songs = songs | self.platform.Songs.filter(uploaded_by__name__icontains=text).distinct()
        songs = songs.distinct()
        if songs.count() >= limit:
            return songs[:limit]
        
        # contributing artists name contains search value
        songs = songs | self.platform.Songs.filter(contributors__name__icontains=text).distinct()
        songs = songs.distinct()
        if songs.count() >= limit:
            return songs[:limit]
        
        # album name contains search value
        songs = songs | self.platform.Songs.filter(album__name__icontains=text).distinct()
        songs = songs.distinct()
        if songs.count() >= limit:
            return songs[:limit]
        
        # album contributors name is exactly search value
        songs = songs | self.platform.Songs.filter(album__contributors__name__iexact=text).distinct()
        songs = songs.distinct()
        if songs.count() >= limit:
            return songs[:limit]

        # album contributors name contains search value
        songs = songs | self.platform.Songs.filter(album__contributors__name__icontains=text).distinct()
        songs = songs.distinct()
        if songs.count() >= limit:
            return songs[:limit]

        return songs[:limit]

    def search_albums(self, text, *args, **kwargs):
        assert text, "method 'search_albums' requires a search value."
        limit = const.SEARCH_LIMIT

        # album name is exactly search value
        albums = self.platform.Albums.filter(name__iexact=text).distinct()
        if albums.count() >= limit:
            return albums[:limit]

        # uploaded by name is exactly search value
        albums = albums | self.platform.Albums.filter(uploaded_by__name__iexact=text).distinct()
        albums = albums.distinct()
        if albums.count() > limit:
            return albums[:limit]
        
        # album contributor name is exactly search value
        albums = albums | self.platform.Albums.filter(contributors__name__iexact=text).distinct()
        albums = albums.distinct()
        if albums.count() > limit:
            return albums[:limit]
        
        # album has a song with a title that is exactly the search value
        albums = albums | self.platform.Albums.filter(song__title__iexact=text).distinct()
        albums = albums.distinct()
        if albums.count() > limit:
            return album[:limit]
        
        # albums name contains the search value
        albums = albums | self.platform.Albums.filter(name__icontains=text).distinct()
        albums = albums.distinct()
        if albums.count() > limit:
            return album[:limit]
        
        # uploaded by name contains the search value
        albums = albums | self.platform.Albums.filter(uploaded_by__name__icontains=text).distinct()
        albums = albums.distinct()
        if albums.count() > limit:
            return album[:limit]
        
        # album contributor name contains the search value
        albums = albums | self.platform.Albums.filter(contributors__name__icontains=text).distinct()
        albums = albums.distinct()
        if albums.count() > limit:
            return album[:limit]

        # album song title contains the search value
        albums = albums | self.platform.Albums.filter(song__title__icontains=text).distinct()
        albums = albums.distinct()
        if albums.count() > limit:
            return album[:limit]

        return albums[:limit]
    
    def search_artists(self, text, *args, **kwargs):
        assert text, "method 'search_artists' requires a search value."

        # filter artists
        artists = self.platform.Artists.filter(
            Q(name__icontains=text) |
            # filter by uploaded albums
            Q(album__name__icontains=text) |
            # filter by uploaded songs
            Q(song_uploaded_by__title__icontains=text) |
            Q(song_uploaded_by__genre__icontains=text)
        ).distinct()

        return artists
    
    def search_playlists(self, text, *args, **kwargs):
        pass
