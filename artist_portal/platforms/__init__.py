from . import *

def get_platform(string):
    platforms = [
        revibe.Revibe,
        youtube.YouTube
    ]

    for platform in platforms:
        if string in platform.strings:
            return platform
    raise ValueError("could not find {} in platform strings".format(string))