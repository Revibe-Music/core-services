class ImageURLMixin:
    def get_image_url(self, obj):
        return obj.image.url
class ArtistImageURLMixin:
    def get_image_url(self, obj):
        return obj.artist.image.url
class AlbumImageURLMixin:
    def get_image_url(self, obj):
        return obj.album.image.url