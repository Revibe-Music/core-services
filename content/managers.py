from django.db import models # models.Manager


class NotHiddenNotDeletedManager(models.Manager):
    def get_queryset(self):
        return super(NotHiddenNotDeletedManager, self).get_queryset().filter(is_displayed=True, is_deleted=False)


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
