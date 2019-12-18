from rest_framework import views, viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response

from artist_portal.viewsets import PlatformViewSet
from artist_portal._helpers.platforms import get_platform
from accounts.permissions import TokenOrSessionAuthentication
from content.mixins import V1Mixin
from content.models import *
from content.serializers import v1 as ser_v1


class ArtistViewset(PlatformViewSet):
    platform = 'Revibe'
    serializer_class = ser_v1.ArtistSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]],
    }

    def get_queryset(self):
        return self.platform.Artists

    @action(detail=True)
    def albums(self, request, pk=None):
        artist = self.get_object()
        queryset = self.platform.Albums.filter(uploaded_by=artist)
        serializer = ser_v1.AlbumSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True)
    def songs(self, request, pk=None):
        artist = self.get_object()
        queryset = self.platform.Songs.filter(uploaded_by=artist)
        serializer = ser_v1.SongSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True)
    def album_contributions(self, request, pk=None):
        artist = self.get_object()
        queryset = self.platform.AlbumContributors.filter(artist=artist)
        serializer = ser_v1.AlbumContributorSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True)
    def song_contributions(self, request, pk=None):
        artist = self.get_object()
        queryset = self.platform.SongContributors.filter(artist=artist)
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
    def songs(self, request, pk=None):
        album = self.get_object()
        queryset = self.platform.Songs.filter(album=ablum)
        serializer = ser_v1.SongSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SongViewSet(PlatformViewSet):
    platform = 'Revibe'
    serializer_class = ser_v1.SongSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]],
    }


class MusicSearch(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    # permission_classes = [TokenOrSessionAuthentication]
    # required_alternate_scopes = {
    #     "GET": [["ADMIN"],["first-party"]],
    # }

    def list(self, request, *args, **kwargs):
        params = request.query_params

        if 'text' not in params.keys():
            return Response({"error": "'text' must be included as a parameter in this request"}, status=status.HTTP_417_EXPECTATION_FAILED)
        text = params['text']
        
        result = {}

        t = params.get('type', False)
        if t:
            if t not in ['songs','albums','artists']:
                return Response({'error': "parameter 'type' must be 'songs', 'albums', or 'artists'."}, status=status.HTTP_400_BAD_REQUEST)

        if (t == 'songs') or (not t):
            result['songs'] = SongSerializer(RevibeSongs.filter(title__icontains=text), many=True).data
        if (t == 'albums') or (not t):
            result['albums'] = AlbumSerializer(RevibeAlbums.filter(name__icontains=text), many=True).data
        if (t == 'artists') or (not t):
            result['artists'] = ArtistSerializer(RevibeArtists.filter(name__icontains=text), many=True).data

        return Response(result ,status=status.HTTP_200_OK)