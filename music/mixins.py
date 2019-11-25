class ImageURLMixin:
    def get_image_url(self, obj):
        try:
            return obj.image.url
        except ValueError as err:
            return ""
        except Exception as err:
            raise err

class ArtistImageURLMixin:
    def get_image_url(self, obj):
        try:
            return obj.artist.image.url
        except ValueError as err:
            return ""
        except Exception as err:
            raise err

class AlbumImageURLMixin:
    def get_image_url(self, obj):
        try:
            return obj.album.image.url
        except ValueError as err:
            return ""
        except Exception as err:
            raise err