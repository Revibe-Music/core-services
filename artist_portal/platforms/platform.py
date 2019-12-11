from artist_portal._errors.random import PlatformNotFoundError
from .revibe import Revibe
from .youtube import YouTube
class Platform:
    platforms = [
        Revibe,
        YouTube,
    ]

    @classmethod
    def get_platform(cls, string):
        for platform in cls.platforms:
            if string in platform.strings:
                return platform

