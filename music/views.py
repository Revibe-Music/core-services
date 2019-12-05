from django.shortcuts import get_object_or_404
from rest_framework import views, viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from oauth2_provider.contrib.rest_framework import *
from music.models import *
from music.queries import *
from music.serializers import *
from music.services import artist_serializers

class ArtistViewSet(viewsets.ModelViewSet):
    queryset = RevibeArtists
    serializer_class = BaseArtistSerializer
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["read"],["read-songs"]],
    }

    @action(detail=True)
    def albums(self, request, pk=None):
        """
        Sends the artist's list of albums (only uploaded albums, not contributions)
        """
        artist = get_object_or_404(self.queryset, pk=pk)
        queryset = Album.objects.filter(uploaded_by=artist)
        serializer = BaseAlbumSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True)
    def top_songs(self, request, pk=None):
        # this is gonna be a bitch
        pass
    
    @action(detail=True)
    def songs(self, request, pk=None):
        """
        Sends the artist's list of songs (only uploaded songs, not contributions)
        """
        artist = get_object_or_404(self.queryset, pk=pk)
        queryset = Song.objects.filter(uploaded_by=artist)
        serializer = BaseSongSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def album_contributions(self, request, pk=None):
        """
        Sends the list of albums that the artist has contributed to
        """
        artist = get_object_or_404(self.queryset, pk=pk)
        queryset = AlbumContributor.objects.filter(artist=artist)
        serializer = AlbumAlbumContributorSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def song_contributions(self, request, pk=None):
        """
        Sends the list of songs that the artist has contributed to
        """
        artist = get_object_or_404(self.queryset, pk=pk)
        queryset = SongContributor.objects.filter(artist=artist).exclude(song__uploaded_by=artist)
        serializer = SongSongContributorSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def test(self, request, pk=None):
        """
        testing how to send multiple querysets in one response
        """
        artist = get_object_or_404(self.queryset, pk=pk)
        queryset = Album.objects.filter(uploaded_by=artist)
        album_serializer = BaseAlbumSerializer(queryset, many=True)
        queryset = AlbumContributor.objects.filter(artist=artist)
        contrib_serializer = AlbumAlbumContributorSerializer(queryset, many=True)
        return Response({
            'albums': album_serializer.data,
            'contribs': contrib_serializer.data
        })

class AlbumViewSet(viewsets.ModelViewSet):
    queryset = RevibeAlbums
    serializer_class = BaseAlbumSerializer
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["read"],["read-albums"]],
        "POST": [["ADMIN"]],
        "PUT": [["ADMIN"]],
        "PATCH": [["ADMIN"]],
        "UPDATE": [["ADMIN"]],
        "DELETE": [["ADMIN"]]
    }

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    @action(detail=True)
    def songs(self, request, pk=None):
        album = get_object_or_404(self.queryset, pk=pk)
        queryset = Song.objects.filter(album=album)
        serializer = BaseSongSerializer(queryset, many=True)
        return Response(serializer.data)

class SongViewSet(viewsets.ModelViewSet):
    queryset = RevibeSongs
    serializer_class = BaseSongSerializer
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["read"],["read-songs"]],
        "POST": [["ADMIN"]],
        "PUT": [["ADMIN"]],
        "PATCH": [["ADMIN"]],
        "UPDATE": [["ADMIN"]],
        "DELETE": [["ADMIN"]]
    }

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

class SongContributorViewSet(viewsets.ModelViewSet):
    queryset = SongContributor.objects.all()
    serializer_class = BaseSongContributorSerialzer
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["read"],["read-songs"]],
        "POST": [["ADMIN"]],
        "PUT": [["ADMIN"]],
        "PATCH": [["ADMIN"]],
        "UPDATE": [["ADMIN"]],
        "DELETE": [["ADMIN"]]
    }

class LibraryViewSet(viewsets.ModelViewSet):
    serializer_class = BaseLibrarySerializer
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["read"],["read-library"]],
        "POST": [["ADMIN"]],
        "DELETE": [["ADMIN"]]
    }

    def get_queryset(self):
        """
        Return the list of saved songs for the current user
        """
        user = self.request.user
        return Library.objects.filter(user=user)
    
    @action(detail=False, methods=['get','post', 'delete'])
    def songs(self, request, *args, **kwargs):

        if request.method == 'GET':
            return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

        elif request.method == 'POST':
            kwargs['context'] = self.get_serializer_context()
            serializer = BaseLibrarySongSerializer(data=request.data, *args, **kwargs)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # print to console if in debug mode
            if settings.DEBUG:
                print(serializer)
                print(serializer.data)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
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
    serializer_class = BasePlaylistSerializer
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["read"],["read-playlist"]],
        "POST": [["ADMIN"]],
        "DELETE": [["ADMIN"]]
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
            return Response(serializer.data)

        elif request.method == 'DELETE':
            serializer = BasePlaylistSongSerializer(data=request.data, *args, **kwargs)
            serializer.is_valid(raise_exception=True)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class MusicSearch(viewsets.GenericViewSet):
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]],
    }

    def list(self, request, *args, **kwargs):
        text = request.data['text']
        songs = BaseSongSerializer(RevibeSongs.filter(title__icontains=text), many=True).data
        albums = BaseAlbumSerializer(RevibeAlbums.filter(name__icontains=text), many=True).data
        artists = BaseArtistSerializer(RevibeArtists.filter(name__icontains=text), many=True).data

        return Response(
            {'songs': songs, 'albums': albums, 'artists': artists},
            status=status.HTTP_200_OK
        )
