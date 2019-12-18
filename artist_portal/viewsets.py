from rest_framework.viewsets import GenericViewSet, ModelViewSet

from artist_portal._helpers.platforms import get_platform

class PlatformViewSet(ModelViewSet):
    def __init__(self, *args, **kwargs):
        super(PlatformViewSet, self).__init__(*args, **kwargs)
        platform = get_platform(self.platform)
        self.platform = platform()
    
    def perform_destroy(self, instance):
        self.platform.destroy(instance)

class GenericPlatformViewSet(GenericViewSet):
    def __init__(self, *args, **kwargs):
        super(GenericPlatformViewSet, self).__init__(*args, **kwargs)
        platform = get_platform(self.platform)
        self.platform = platform()
