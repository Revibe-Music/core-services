from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet

from revibe._helpers.platforms import get_platform

class PlatformViewSet(ModelViewSet):
    def __init__(self, *args, **kwargs):
        super(PlatformViewSet, self).__init__(*args, **kwargs)
        self.platform = get_platform(self.platform)
    
    def perform_destroy(self, instance):
        self.platform.destroy(instance)

class ReadOnlyPlatformViewSet(ReadOnlyModelViewSet):
    def __init__(self, *args, **kwargs):
        super(ReadOnlyModelViewSet, self).__init__(*args, **kwargs)
        self.platform = get_platform(self.platform)
    
    def perform_destroy(self, instance):
        self.platform.destroy(instance)

class GenericPlatformViewSet(GenericViewSet):
    def __init__(self, *args, **kwargs):
        super(GenericPlatformViewSet, self).__init__(*args, **kwargs)
        self.platform = get_platform(self.platform)
