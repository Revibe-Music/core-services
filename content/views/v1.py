from django.db.models import Q
from rest_framework import views, viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response

from revibe.pagination import CustomLimitOffsetPagination
from revibe.viewsets import *
from revibe.utils.params import get_url_param
from revibe._errors.network import ProgramError, ExpectationFailedError
from revibe._helpers import const, responses
from revibe._helpers.platforms import get_platform

from accounts.permissions import TokenOrSessionAuthentication
from content import browse
from content.mixins import V1Mixin
from content.models import *
from content.serializers import v1 as ser_v1
from content.utils.models import get_tag

# -----------------------------------------------------------------------------


class ArtistViewset(PlatformViewSet):
    platform = 'Revibe'
    serializer_class = ser_v1.ArtistSerializer
    pagination_class = CustomLimitOffsetPagination
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

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ser_v1.AlbumSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ser_v1.AlbumSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_name="cnt-artist-songs")
    def songs(self, request, pk=None):
        artist = self.get_object()
        queryset = self.platform.Songs.filter(uploaded_by=artist)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ser_v1.SongSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ser_v1.SongSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_name="cnt-artist-album-contributions")
    def album_contributions(self, request, pk=None):
        artist = self.get_object()
        queryset = self.platform.AlbumContributors.filter(artist=artist, primary_artist=False)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ser_v1.AlbumContributorSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ser_v1.AlbumContributorSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_name="cnt-artist-song-contributions")
    def song_contributions(self, request, pk=None):
        artist = self.get_object()
        queryset = self.platform.SongContributors.filter(artist=artist, primary_artist=False)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ser_v1.SongContributorSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ser_v1.SongContributorSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True)
    def top_songs(self, request, pk=None):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


class AlbumViewSet(PlatformViewSet):
    platform = 'Revibe'
    serializer_class = ser_v1.AlbumSerializer
    pagination_class = CustomLimitOffsetPagination
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
    pagination_class = CustomLimitOffsetPagination
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
        limit = const.SEARCH_LIMIT

        # artsit name is exactly the search value
        artists = self.platform.Artists.filter(name__iexact=text).distinct()
        if artists.count() > limit:
            return artists[:limit]
        
        # album or song is exactly the search value
        artists = artists | self.platform.Artists.filter(
            Q(song_uploaded_by__title__iexact=text) |
            Q(album__name__iexact=text)
        ).distinct()
        artists = artists.distinct()
        if artists.count() > limit:
            return artsits[:limit]
        
        # artsit name contains the search value
        artists = artists | self.platform.Artists.filter(name__icontains=text).distinct()
        artists = artists.distinct()
        if artists.count() > limit:
            return artists[:limit]
        
        # album or song contains the search value
        artists = artists | self.platform.Artists.filter(
            Q(song_uploaded_by__title__icontains=text) |
            Q(album__name__icontains=text)
        ).distinct()
        artists = artists.distinct()
        if artists.count() > limit:
            return artists[:limit]

        return artists[:limit]
    
    def search_playlists(self, text, *args, **kwargs):
        pass

    @action(detail=False, methods=['get'], url_path="tags", url_name="search-tags")
    def tags(self, request, *args, **kwargs):
        params = request.query_params

        if 'text' not in params:
            raise ExpectationFailedError("Param 'text' not in query params")
        text = get_url_param(params, 'text')
        content = get_url_param(params, 'content')
        if (content == None) or (content not in ['songs', 'albums']):
            content = 'songs'
        
        objs = self.search_tags(text, content)
        data = {
            content: objs.data
        }

        return responses.OK(data=data)

    def search_tags(self, text, obj, *args, **kwargs):
        """
        return songs/albums by the tag that was sent
        """
        # get the tag
        tag = get_tag(text)
        objs = []

        # which object to search
        if obj.lower() == 'songs':
            objs = ser_v1.SongSerializer(tag.songs.all(), many=True)
        elif obj.lower() == 'albums':
            objs = ser_v1.AlbumSerializer(tag.albums.all(), many=True)
        else:
            raise ProgramError("Must send either 'songs' or 'albums' to 'search_tags'.")

        return objs

    @action(detail=False, methods=['get'], url_path="artists", url_name="search-artists")
    def artists(self, request, *args, **kwargs):
        """
        Special endpoint just for artists to be able to search other artsists
        when adding contributors.
        """
        params = request.query_params

        if 'text' not in params:
            return responses.SERIALIZER_ERROR_RESPONSE(detail="missing parameter 'text'.")
        text = params['text']

        artists = self.exclusive_artist_search(text)
        serializer = ser_v1.ArtistSerializer(artists, many=True)

        return responses.OK(serializer=serializer)

    def exclusive_artist_search(self, text, *args, **kwargs):
        assert (text) and (text != " "), "method 'exclusive_artist_search' requires a search value."
        limit = const.SEARCH_LIMIT
        # perform search
        if len(text) == 1:
            # artist name begins with the search value
            artists = self.platform.Artists.filter(name__istartswith=text).distinct()
        else:
            # artist name is exactly the search value
            artists = self.platform.Artists.filter(name__iexact=text).distinct()
            if artists.count() >= limit:
                return artists[:limit]
            
            # artist name contains the search value
            artists = artists | self.platform.Artists.filter(name__icontains=text).distinct()
            artists = artists.distinct()
            if artists.count() >= limit:
                return artists[:limit]
            
        return artists[:limit]


class Browse(GenericPlatformViewSet):
    platform = 'Revibe'
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]]
    }

    def list(self, request, *args, **kwargs):
        return responses.NOT_IMPLEMENTED()

    @action(detail=False, methods=['get'], url_path="top-songs-all-time", url_name="top-songs-all-time")
    def top_songs_all_time(self, request, *args, **kwargs):
        serializer = browse.top_songs_all_time()
        return responses.OK(serializer=serializer)

    @action(detail=False, methods=['get'], url_path="top-albums-all-time", url_name="top-albums-all-time")
    def top_albums_all_time(self, request, *args, **kwargs):
        serializer = browse.top_albums_all_time()
        return responses.OK(serializer=serializer)

