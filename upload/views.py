from django.contrib.auth.models import User, Group
from .models import *
from rest_framework import viewsets
from .serializers import *


# class UserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = User.objects.all().order_by('-date_joined')
#     serializer_class = UserSerializer


# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer

class SongViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows songs to be viewed or edited.
    """
    queryset = Song.objects.all()
    serializer_class = SongSerializer

class ArtistViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows songs to be viewed or edited.
    """
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer

class AlbumViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows songs to be viewed or edited.
    """
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
