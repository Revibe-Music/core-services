def rename_song(instance, filename):
    ext = filename.split('.')[-1]
    path = "audio/songs/"
    if instance.uri:
        return "{path}{uri}.{ext}".format(path=path, uri=instance.uri, ext=ext)
    else:
        return path + filename

def rename_image(instance, filename):
    ext = filename.split('.')[-1]
    path = "audio/images/"
    if instance.uri:
        return "{path}{uri}.{ext}".format(path=path, uri=instance.uri, ext=ext)
    else:
        return path + filename