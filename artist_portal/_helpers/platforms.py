from artist_portal.platforms.platforms import *
from artist_portal._errors.platforms import PlatformNotFoundError

def get_platform(string):
    platforms = [Revibe, YouTube]
    for platform in platforms:
        if string in platform.strings:
            return platform
    raise PlatformNotFoundError("Could not determine the platform based on the input {}".format(string))
