from rest_framework.serializers import SerializerMethodField
class ImageURLMixin:
    image = SerializerMethodField('get_image_url')
    def get_image_url(self, obj):
        return obj.image.url