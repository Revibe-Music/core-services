import os

# -----------------------------------------------------------------------------

def rename_song(instance, filename):
    ext = filename.split('.')[-1]
    path = "audio/songs"
    if instance.uri:
        return "{path}/{uri}.{ext}".format(path=path, uri=instance.uri, ext=ext)
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

def custom_image_upload(instance, filename):
    ext = filename.split('.')[-1]

    folder = instance.obj.__class__.__name__
    uri = str(instance.obj.uri)

    root_path = os.path.join("images", folder, uri)

    if instance.is_original:
        path = os.path.join(root_path, "inputs", "original."+ext)
    else:
        path = os.path.join(root_path, "outputs", ext, filename)
    
    return path

def custom_audio_upload(instance, filename):
    ext = filename.split('.')[-1]

    song = instance.song
    uri = str(song.uri)

    root_path = os.path.join("audio", "songs", uri)

    if instance.is_original:
        path = os.path.join(root_path, "inputs", "original."+ext)
    else:
        path = os.path.join(root_path, "outputs", ext, filename)
    
    return path
