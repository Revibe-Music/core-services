from faker import Faker
from . import models


class SongFactory(factory.Factory):
    class Meta:
        model = models.Song

class ArtistFactory(factory.Factory):
    class Meta:
        model = models.Artist

class AlbumFactory(factory.Factory):
    class Meta:
        model = models.Album

class AlbumContributorFactory(factory.Factory):
    class Meta:
        model = models.AlbumContributor

class SongContributorFactory(factory.Factory):
    class Meta:
        model = models.SongContributor

class LibraryFactory(factory.Factory):
    class Meta:
        model = models.Library

class PlaylistFactory(factory.Factory):
    class Meta:
        model = models.Playlist
