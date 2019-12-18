from django.db import models

class DisplayModelManager(models.Manager):
    def get_queryset(self):
        return super(DisplayModelManager, self).get_queryset().filter(is_displayed=True, is_deleted=False)

class HiddenModelManager(models.Manager):
    def get_queryset(self):
        return super(HiddenModelManager, self).get_queryset().filter(is_deleted=False)
