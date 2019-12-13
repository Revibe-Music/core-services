from django.db import models

def rename_song(instance, filename):
    ext = filename.split('.')[-1]
    path = "audio/songs/"
    if instance.uri:
        return "{path}{uri}.{ext}".format(path=path, uri=instance.uri, ext=ext)
    else:
        return path + filename

def rename_image(instance, filename):
    folder = instance.__class__.__name__
    ext = filename.split('.')[-1]
    path = "images/{}/".format(folder)
    if instance.uri:
        return "{path}{uri}.{ext}".format(path=path, uri=instance.uri, ext=ext)
    else:
        return path + filename

class DisplayModelManager(models.Manager):
    def get_queryset(self):
        return super(DisplayModelManager, self).get_queryset().filter(is_displayed=True, is_deleted=False)

class HiddenModelManager(models.Manager):
    def get_queryset(self):
        return super(HiddenModelManager, self).get_queryset().filter(is_deleted=False)
