from django.db import models

class DisplayModelManager(models.Manager):
    def get_queryset(self):
        return super(DisplayModelManager, self).get_queryset().filter(is_displayed=True, is_deleted=False)

class HiddenModelManager(models.Manager):
    def get_queryset(self):
        return super(HiddenModelManager, self).get_queryset().filter(is_deleted=False)

class SongContributorManager(models.Manager):
    def get_queryset(self):
        return super(SongContributorManager, self).get_queryset().filter(song__is_deleted=False)

class AlbumContributorManager(models.Manager):
    def get_queryset(self):
        return super(AlbumContributorManager, self).get_queryset().filter(album__is_deleted=False)
