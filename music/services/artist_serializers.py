from music.mixins import ArtistImageURLMixin
from music.models import *
from rest_framework import serializers

# class ArtistAlbumSerializer(BaseAlbumSerializer):
#     class Meta(BaseAlbumSerializer.Meta):
#         fields = [
#             'id',
#             'name',
#             'image',
#             'platform',
#             'album_to_artist'
#         ]

# class ArtistSongSerializer(BaseSongSerializer):
#     class ContributorSerializer(BaseSongContributorSerialzer):
#         song = None
#         class Meta(BaseSongContributorSerialzer.Meta):
#             fields = [
#                 'artist',
#                 'contribution_type'
#             ]
#     album = ArtistAlbumSerializer(many=False)
#     song_to_artist = ContributorSerializer(many=True)
#     class Meta(BaseSongSerializer.Meta):
#         fields = [
#             'id',
#             'uri',
#             'title',
#             'genre',
#             'duration',
#             'platform',
#             'uploaded_date',
#             'album',
#             'song_to_artist'
#         ]

# class ArtistAlbumContributorSerializer(serializers.ModelSerializer):
#     album = ArtistAlbumSerializer(many=False)
#     class Meta:
#         model = AlbumContributor
#         fields = [
#             'contribution_type',
#             'album'
#         ]

# class ArtistSongContributorSerializer(serializers.ModelSerializer):
#     song = ArtistSongSerializer(many=False)
    
#     class Meta:
#         model = SongContributor
#         fields = [
#             'contribution_type',
#             'song'
#         ]
