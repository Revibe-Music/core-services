from django.db import models # models.Manager


class NotHiddenNotDeletedManager(models.Manager):
    def get_queryset(self):
        return super(NotHiddenNotDeletedManager, self).get_queryset().filter(is_displayed=True, is_deleted=False)

class NotDeletedManager(models.Manager):
    def get_queryset(self):
        return super(NotDeletedManager, self).get_queryset().filter(is_deleted=False)

class AlbumContributorManager(models.Manager):
    def get_queryset(self):
        return super(AlbumContributorManager, self).get_queryset() \
            .filter(album__is_displayed=True, album__is_deleted=False)

class HiddenAlbumContributorManager(models.Manager):
    def get_queryset(self):
        return super(HiddenAlbumContributorManager, self).get_queryset() \
            .filter(album__is_deleted=False)

class SongContributorManager(models.Manager):
    def get_queryset(self):
        return super(SongContributorManager, self).get_queryset() \
            .filter(song__is_displayed=True, song__is_deleted=False)

class HiddenSongContributorManager(models.Manager):
    def get_queryset(self):
        return super(HiddenSongContributorManager, self).get_queryset() \
            .filter(song__is_deleted=False)

class AlbumContributionDisplayManager(AlbumContributorManager):
    def get_queryset(self):
        super(AlbumContributionDisplayManager, self).get_queryset() \
            .filter(approved=True)

class SongContributionDisplayManager(SongContributorManager):
    def get_queryset(self):
        super(SongContributionDisplayManager, self).get_queryset() \
            .filter(approved=True)
