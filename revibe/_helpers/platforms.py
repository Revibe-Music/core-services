from revibe.platforms.platforms import *
from revibe._errors.platforms import PlatformNotFoundError

linked_platforms = [
    Revibe,
    YouTube,
    Spotify,
]

def get_platform(string):
    for platform in linked_platforms:
        if string in platform.strings:
            return platform
    raise PlatformNotFoundError("Could not determine the platform based on the input {}".format(string))
