from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import views, viewsets, permissions as perm, generics, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from oauth2_provider.contrib.rest_framework import *

from logging import getLogger
logger = getLogger(__name__)

from revibe.pagination import CustomLimitOffsetPagination
from revibe._errors import data, network
from revibe._helpers import responses
from revibe._helpers.debug import debug_print
from revibe.platforms import get_platform, linked_platforms
from revibe.utils.params import get_url_param

from accounts.permissions import TokenOrSessionAuthentication
from content.serializers.v1 import *
from music.mixins import Version1Mixin
from music.models import *
from music.serializers.v1 import *
from music.utils.models.playlist import bulk_add_songs_to_playlist

# -----------------------------------------------------------------------------

@method_decorator(csrf_exempt, name="dispatch")
class LibraryViewSet(viewsets.ModelViewSet, Version1Mixin):
    serializer_class = LibrarySerializer
    pagination_class = CustomLimitOffsetPagination
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]],
        "POST": [["ADMIN"],["first-party"]],
        "DELETE": [["ADMIN"],["first-party"]],
    }

    def get_queryset(self):
        """
        Return the list of saved songs for the current user
        """
        user = self.request.user
        return Library.objects.filter(user=user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        params = request.query_params
        if 'library' in params.keys():
            library = params['library']
            for platform in linked_platforms:
                if library in platform.strings:
                    queryset = queryset.filter(platform=platform())
                    break

        serializer = self.get_serializer(queryset, many=True)
        return responses.OK(serializer)

    @action(detail=False, methods=['get','post', 'delete'], url_name='songs')
    def songs(self, request, *args, **kwargs):
        """
        """

        if request.method == 'GET':
            params = request.query_params

            # parameter 'platform' required in request
            if 'platform' not in params:# and 'id' not in params:
                raise data.ParameterMissingError("parameter 'platform' not found")
            platform = params['platform']

            try:
                library = self.get_queryset().get(platform=platform)
            except Library.DoesNotExist as e:
                raise network.NotFoundError()

            songs = library.library_to_song.all()
            page = self.paginate_queryset(songs)
            if page is not None:
                serializer = ReadOnlyLibrarySongSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = ReadOnlyLibrarySongSerializer(songs, many=True)
            return responses.OK(serializer=serializer)


        elif request.method == 'POST':
            kwargs['context'] = self.get_serializer_context()
            # kwargs['version'] = self.get_version()
            platform = get_platform(request.data['platform'])

            # instance = platform.save(request.data, *args, **kwargs)
            instance = platform.save_song_to_library(request, *args, **kwargs)
            serializer = LibrarySongSerializer(instance=instance, *args, **kwargs)

            return responses.CREATED(serializer=serializer)


        elif request.method == 'DELETE':
            kwargs['context'] = self.get_serializer_context()
            serializer = LibrarySongSerializer(data=request.data, *args, **kwargs)
            if serializer.is_valid():
                serializer.delete(data=request.data)
                return responses.DELETED()
            else:
                return responses.SERIALIZER_ERROR_RESPONSE(serializer=serializer)
        else:
            return responses.DEFAULT_400_RESPONSE()
    
    @action(detail=False, methods=['get','post', 'delete'])
    def albums(self, request, *args, **kwargs):

        # get the album from the ID if it's not a GET request
        album = None
        if request.method != 'GET':
            if 'album_id' not in request.data.keys():
                raise network.BadRequestError("Field 'album_id' cannot be null")
            try:
                album = Album.hidden_objects.get(pk=request.data['album_id'])
            except Album.DoesNotExist:
                raise network.NotFoundError(f"Album with ID '{request.data['album_id']}' not found")

            kwargs['context'] = self.get_serializer_context()

        # handle all the requests
        if request.method == 'GET':
            return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

        elif request.method == 'POST':
            # add all songs to the library
            for song in album.song_set.all():
                serializer = LibrarySongSerializer(data={'song_id': song.id}, *args, **kwargs)
                serializer.is_valid(raise_exception=True)
                serializer.save()

            return responses.CREATED()

        elif request.method == 'DELETE':
            # delete all songs from the library
            for song in album.song_set.all():
                data = {'song_id': song.id}
                serializer = LibrarySongSerializer(data=data, *args, **kwargs)
                serializer.is_valid(raise_exception=True)
                serializer.delete(data=data)

            return responses.DELETED()

        else:
            return Reponse(status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name="dispatch")
class PlaylistViewSet(viewsets.ModelViewSet):
    serializer_class = PlaylistSerializer
    pagination_class = CustomLimitOffsetPagination
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]],
        "POST": [["ADMIN"],["first-party"]],
        "PATCH": [["ADMIN"],["first-party"]],
        "DELETE": [["ADMIN"],["first-party"]],
    }

    def get_queryset(self, public=False):
        """
        Return the current user's playlists
        """
        user = self.request.user
        if not public:
            return Playlist.objects.filter(user=user)
        else:
            return Playlist.objects.filter(
                Q(user=user) | Q(is_public=True)
            )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return responses.CREATED(serializer=serializer)
        else:
            return responses.SERIALIZER_ERROR_RESPONSE(serializer=serializer)
        return responses.DEFAULT_400_RESPONSE()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.user:
            raise network.ForbiddenError("You cannot delete this playlist")

        self.perform_destroy(instance)
        return responses.DELETED()

    def check_playlist_edit_permissions(self, playlist, user):
        """
        Checks if the current user is allowed to add/remove content from the
        given playlist.
        """
        if user != playlist.user:
            raise network.ForbiddenError("You cannot make changes to this playlist")

    @action(detail=False, methods=['get','post', 'delete'])
    def songs(self, request, pk=None, *args, **kwargs):        
        kwargs['context'] = self.get_serializer_context()

        if request.method == 'GET':
            params = request.query_params

            playlist_id = get_url_param(params, "playlist_id")
            if playlist_id == None:
                raise data.ParameterMissingError("parameter 'playlist_id' not found")

            queryset = self.get_queryset(public=True)

            try:
                playlist = queryset.get(id=playlist_id)
            except Playlist.DoesNotExist:
                raise network.NotFoundError("Could not find the specified playlist")

            songs = playlist.playlist_to_song.all()
            page = self.paginate_queryset(songs)
            if page is not None:
                # serializer = SongSerializer(page, many=True)
                serializer = PlaylistSongSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            # serializer = SongSerializer(songs, many=True)
            serializer = PlaylistSongSerializer(page, many=True)
            return responses.OK(serializer=serializer)

        elif request.method == 'POST':
            platform = get_platform(request.data.get('platform', 'revibe'))

            playlist_id = request.data.get('playlist_id', None)
            if playlist_id == None:
                raise network.BadRequestError("Field 'playlist_id' not found")
            try:
                playlist = Playlist.objects.get(id=playlist_id)
            except Playlist.DoesNotExist:
                raise network.NotFoundError()

            self.check_playlist_edit_permissions(playlist, request.user)

            instance = platform.save_song_to_playlist(request, playlist, *args, **kwargs)
            serializer = PlaylistSongSerializer(instance=instance, *args, **kwargs)

            return responses.CREATED(serializer=serializer)

        elif request.method == 'DELETE':
            try:
                song = Song.objects.get(id=request.data['song_id'])
                playlist = Playlist.objects.get(id=request.data['playlist_id'])
            except (Song.DoesNotExist, Playlist.DoesNotexist) as e:
                raise network.NotFoundError()
            self.check_playlist_edit_permissions(playlist, request.user)

            instance = PlaylistSong.objects.get(playlist=playlist, song=song)
            instance.delete()

            return responses.DELETED()

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path="songs/bulk", url_name="songs-bulk")
    def bulk_add_songs(self, request, *args, **kwargs):
        playlist_id = request.data.pop('playlist_id', None)
        songs = request.data.pop('songs', None)

        if playlist_id == None or songs == None:
            raise network.BadRequestError("Required fields missing")

        result = bulk_add_songs_to_playlist(playlist_id, songs)

        return responses.CREATED(data=result)


