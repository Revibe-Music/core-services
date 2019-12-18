from django.db import models # models.Manager


class NotHiddenNotDeletedManager(models.Manager):
    def get_queryset(self):
        return super(NotHiddenNotDeletedManager, self).get_queryset().filter(is_displayed=True, is_deleted=False)

class NotDeletedManager(models.Manager):
    def get_queryset(self):
        return super(NotDeletedManager, self).get_queryset().filter(is_deleted=False)
