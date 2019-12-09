from django.db import models
from django.conf import settings
# from music.models import Song

# Create your models here.

class Streams(models.Model):
    song = models.ForeignKey('music.Song', on_delete=models.CASCADE, related_name='song_streams', null=False, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_streams", on_delete=models.SET_NULL, null=True, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True, null=False, blank=True, editable=False)
    stream_duration = models.IntegerField()
    stream_percentage = models.DecimalField()
    is_downloaded = models.BooleanField()
    is_saved = models.BooleanField()
    streamed_from_lat = models.DecmialField(max_digits=9, decimal_places=6)
    streamed_from_long = models.DecmialField(max_digits=9, decimal_places=6)
    device = models.CharField(max_length=255)

