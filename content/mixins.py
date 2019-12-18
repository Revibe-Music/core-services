class V1Mixin:
    def get_version(**kwargs):
        kwargs['version'] = 'v1'
        return kwargs

class V2Mixin:
    def get_version(**kwargs):
        kwargs['version'] = 'v2'
        return kwargs