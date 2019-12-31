from django.shortcuts import get_object_or_404
from rest_framework import views, viewsets, permissions as perm, generics, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from oauth2_provider.contrib.rest_framework import *

from artist_portal._helpers import responses
from artist_portal._helpers.debug import debug_print
from artist_portal._helpers.platforms import get_platform, linked_platforms
from accounts.permissions import TokenOrSessionAuthentication
from content.serializers.v1 import *
from music.mixins import Version1Mixin
from music.models import *
from music.serializers.v1 import *


class LibraryViewSet(viewsets.ModelViewSet, Version1Mixin):
    serializer_class = LibrarySerializer
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

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return responses.OK(serializer)

    @action(detail=False, methods=['get','post', 'delete'], url_name='songs')
    def songs(self, request, *args, **kwargs):
        """
        """

        if request.method == 'GET':
            return responses.NOT_IMPLEMENTED()

        elif request.method == 'POST':
            kwargs['context'] = self.get_serializer_context()
            # kwargs['version'] = self.get_version()
            platform = get_platform(request.data['platform'])

            # serializer = platform().save_song_to_library(data=request.data, *args, **kwargs)
            serializer = LibrarySongSerializer(data=request.data, *args, **kwargs)
            if serializer.is_valid():
                serializer.save()
                return responses.CREATED(serializer)
            else:
                return responses.SERIALIZER_ERROR_RESPONSE(serializer)
            return responses.DEFAULT_400_RESPONSE()

        elif request.method == 'DELETE':
            kwargs['context'] = self.get_serializer_context()
            serializer = BaseLibrarySongSerializer(data=request.data, *args, **kwargs)
            serializer.is_valid(raise_exception=True)
            serializer.delete(data=request.data)
            
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get','post', 'delete'])
    def albums(self, request, *args, **kwargs):

        # get the album from the ID if it's not a GET request
        album = None
        if request.method != 'GET':
            if settings.DEBUG:
                print(request.data)
            album = get_object_or_404(Album.objects.all(), pk=request.data['album_id'])
            if settings.DEBUG:
                print(album)

            kwargs['context'] = self.get_serializer_context()

        # handle all the requests
        if request.method == 'GET':
            return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
        
        elif request.method == 'POST':
            # add all songs to the library
            for song in album.song_set.all():
                serializer = BaseLibrarySongSerializer(data={'song_id': song.id}, *args, **kwargs)
                serializer.is_valid(raise_exception=True)
                serializer.save()

            return Response(status=status.HTTP_201_CREATED)
        
        elif request.method == 'DELETE':
            # delete all songs from the library
            for song in album.song_set.all():
                data = {'song_id': song.id}
                serializer = BaseLibrarySongSerializer(data=data, *args, **kwargs)
                serializer.is_valid(raise_exception=True)
                serializer.delete(data=data)
            
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            return Reponse(status=status.HTTP_400_BAD_REQUEST)

class PlaylistViewSet(viewsets.ModelViewSet):
    serializer_class = PlaylistSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]],
        "POST": [["ADMIN"],["first-party"]],
        "DELETE": [["ADMIN"],["first-party"]],
    }

    def get_queryset(self):
        """
        Return the current user's playlists
        """
        user = self.request.user
        return Playlist.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post', 'delete'])
    def songs(self, request, pk=None, *args, **kwargs):        
        kwargs['context'] = self.get_serializer_context()

        if request.method == 'POST':
            serializer = BasePlaylistSongSerializer(data=request.data, *args, **kwargs)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            serializer = BasePlaylistSongSerializer(data=request.data, *args, **kwargs)
            serializer.is_valid(raise_exception=True)
            serializer.delete(data=request.data, *args, **kwargs)

            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

