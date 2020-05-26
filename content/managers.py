from django.db import models # models.Manager
from django.db.models import Q
from django.utils.timezone import now

# -----------------------------------------------------------------------------

# base display objects
class NotHiddenNotDeletedManager(models.Manager):
    def get_queryset(self):
        return super(NotHiddenNotDeletedManager, self) \
            .get_queryset().filter(
                is_displayed=True,
                is_deleted=False,
                uploaded_by__artist_profile__hide_all_content=False
            )

# album display objects
class AlbumNotHiddenNotDeletedManager(NotHiddenNotDeletedManager):
    def get_queryset(self):
        return super(AlbumNotHiddenNotDeletedManager, self) \
            .get_queryset().filter(
                Q(date_published=None) | Q(date_published__lte=now())
            )


# song display objects
class SongNotHiddenNotDeletedManager(NotHiddenNotDeletedManager):
    def get_queryset(self):
        return super(SongNotHiddenNotDeletedManager, self) \
            .get_queryset().filter(
                Q(album__is_displayed=True),
                Q(album__is_deleted=False),
                Q(album__date_published=None) | Q(album__date_published__lte=now())
            )


# artist display objects
class ArtistDisplayManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            Q(artist_profile__hide_all_content=False)
        )


# song hidden objects
class NotDeletedManager(models.Manager):
    def get_queryset(self):
        return super(NotDeletedManager, self).get_queryset().filter(is_deleted=False)


# album contributor managers:
class AlbumContributorManager(models.Manager):
    def get_queryset(self):
        return super(AlbumContributorManager, self).get_queryset() \
            .filter(album__is_displayed=True, album__is_deleted=False)


class HiddenAlbumContributorManager(models.Manager):
    def get_queryset(self):
        return super(HiddenAlbumContributorManager, self).get_queryset() \
            .filter(album__is_deleted=False)


class AlbumContributorDisplayManager(AlbumContributorManager):
    def get_queryset(self):
        return super(AlbumContributorDisplayManager, self).get_queryset() \
            .filter(approved=True, album__is_deleted=False)


# song contributor managers
class SongContributorManager(models.Manager):
    def get_queryset(self):
        return super(SongContributorManager, self).get_queryset() \
            .filter(song__is_displayed=True, song__is_deleted=False)


class HiddenSongContributorManager(models.Manager):
    def get_queryset(self):
        return super(HiddenSongContributorManager, self).get_queryset() \
            .filter(song__is_deleted=False)


class SongContributorDisplayManager(SongContributorManager):
    def get_queryset(self):
        return super(SongContributorDisplayManager, self).get_queryset() \
            .filter(approved=True, song__is_deleted=False)


class GenreManager(models.Manager):
    def get_or_create(self, text):
        text = text.lower()
        try:
            genre = self.get(text=text)
        except:
            genre = self.create(text=text)
        
        return genre


# search managers
class SearchManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('model', 'order')

class AlbumSearchManager(SearchManager):
    def get_queryset(self):
        return super().get_queryset().filter(model='album')

class ArtistSearchManager(SearchManager):
    def get_queryset(self):
        return super().get_queryset().filter(model='artist')

class GenreSearchManager(SearchManager):
    def get_queryset(self):
        return super().get_queryset().filter(model='genre')

class SongSearchManager(SearchManager):
    def get_queryset(self):
        return super().get_queryset().filter(model='song')

class TagSearchManager(SearchManager):
    def get_queryset(self):
        return super().get_queryset().filter(model='tag')


