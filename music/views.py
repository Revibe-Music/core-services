from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from oauth2_provider.contrib.rest_framework import *
from .models import *
from .serializers import *
from .services import artist_serializers


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.filter(platform="Revibe")
    serializer_class = BaseArtistSerializer
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["read"],["read-songs"]]
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
        serializer = artist_serializers.ArtistSongSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def album_contributions(self, request, pk=None):
        """
        Sends the list of albums that the artist has contributed to
        """
        artist = get_object_or_404(self.queryset, pk=pk)
        queryset = AlbumContributor.objects.filter(artist=artist)
        serializer = artist_serializers.ArtistAlbumContributorSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def song_contributions(self, request, pk=None):
        """
        Sends the list of songs that the artist has contributed to
        """
        artist = get_object_or_404(self.queryset, pk=pk)
        queryset = SongContributor.objects.filter(artist=artist)
        serializer = artist_serializers.ArtistSongContributorSerializer(queryset, many=True)
        return Response(serializer.data)


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = BaseAlbumSerializer
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["read"],["read-albums"]]
    }

    # @action(detail=True)
    # def songs(self, request, pk=None):
    #     album = get_object_or_404(self.queryset, pk=pk)
    #     queryset = Song.objects.filter(album=album)
    #     serializer = album_serializers.AlbumSongSerializer(queryset, many=True)
    #     return Response(serializer.data)

class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = BaseSongSerializer
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["read"],["read-songs"]]
    }

class LibraryViewSet(viewsets.ModelViewSet):
    serializer_class = BaseLibrarySerializer
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["read"],["read-library"]]
    }

    def get_queryset(self):
        """
        Return the list of saved songs for the current user
        """
        user = self.request.user
        return Library.objects.filter(user=user)

# @todo replace api_view functions with rest Framework viewSets

# @api_view(['GET'])
# def get_platform_songs(request):
#     data = request.GET.urlencode()
#     platform = request.GET.get('platform')
#     user = request.user
#     if Library.objects.filter(user=user, platform=platform).exists():
#         library = Library.objects.get(user=user, platform=platform)
#         songs = library.getSongs()
#         return Response({"platform": platform, "songs": songs}, status=status.HTTP_200_OK)
#
#     return Response({"platform": platform, "songs": []}, status=status.HTTP_200_OK)
#
# @api_view(['POST'])
# def save_song(request):
#     try:
#         body = json.loads(request.body.decode('utf-8'))
#         platform = body.get("platform")
#         song = body.get("song")
#         user = request.user
#
#         if Library.objects.filter(user=user, platform=platform).exists():
#             library = Library.objects.get(user=user, platform=platform)
#             new_song = Song()
#             new_song.library = library
#             new_song.name = song["name"]
#             new_song.song_id = song["songID"]
#             new_song.artist = song["artist"]
#             new_song.artist_uri = song["artistUri"]
#             new_song.album_art = song["albumArt"]
#             new_song.uri = song["uri"]
#
#             if "album" in song.keys():
#                 new_song.album = song["album"]
#             if "albumUri" in song.keys():
#                 new_song.album_uri = song["albumUri"]
#             if "dateSaved" in song.keys():
#                 new_song.date_saved = song["dateSaved"]
#             if "duration" in song.keys():
#                 new_song.duration = song["duration"]
#             new_song.save()
#
#             return Response({"message": "Song successfully saved."},status=status.HTTP_200_OK)
#
#         return Response({"message": "User does not have a "+ platform + " library."},status=status.HTTP_200_OK)
#
#     except:
#         return Response({"error": "User not found"},status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['POST'])
# def remove_song(request):
#     try:
#         body = json.loads(request.body.decode('utf-8'))
#         platform = body.get("platform")
#         song = body.get("song")
#         user = request.user
#         if Library.objects.filter(user=user, platform=platform).exists():
#             library = Library.objects.get(user=user, platform=platform)
#             if Song.objects.filter(library=library,name=song["name"],artist=song["artist"],uri=song["uri"]).exists():
#                 Song.objects.get(library=library,name=song["name"],artist=song["artist"],uri=song["uri"]).delete()
#
#                 return Response({"message": "Song successfully removed."}, status=status.HTTP_200_OK)
#
#             return Response({"message": "Song '"+song["name"]+"' does not exist in "+ str(library)}, status=status.HTTP_200_OK)
#
#         return Response({"message": "User does not have a "+ platform + " library."},status=status.HTTP_200_OK)
#
#     except:
#         return Response({"error": "User not found"},status=status.HTTP_400_BAD_REQUEST)
