from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from oauth2_provider.contrib.rest_framework import *
from .models import *
from .serializers import *
from .services import artist_serializers


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    serializer_action_classes = {
        # 'retrieve': artist_serializers.ArtistDetailSerializer
    }
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["read"],["read-songs"]]
    }

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()
        
    @action(detail=True)
    def albums(self, request, pk=None):
        uploaded_albums = Album.objects.filter(uploaded_by=pk)
        print(uploaded_albums)

        serializer = self.get_serializer(uploaded_albums)
        print(serializer)
        return Response(serializer.data)

class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["read"],["read-albums"]]
    }

class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["read"],["read-songs"]]
    }

class LibraryViewSet(viewsets.ModelViewSet):
    serializer_class = LibrarySerializer
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
