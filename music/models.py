from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from revibe.utils.classes import default_repr

# -----------------------------------------------------------------------------

class Library(models.Model):
    platform = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    songs = models.ManyToManyField('content.song', through='LibrarySong', related_name='library_songs')

    class Meta:
        verbose_name = "library"
        verbose_name_plural = "libraries"

    def __str__(self):
        return "{} on {}".format(self.user, self.platform)

    def __repr__(self):
        return default_repr(self)


class Playlist(models.Model):
    name = models.CharField("Name", null=True, blank=False, max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    songs = models.ManyToManyField('content.song', through='PlaylistSong', related_name='playlist_songs')

    is_public = models.BooleanField(null=False, blank=True, default=False)
    followers = models.ManyToManyField(
        to='accounts.CustomUser',
        related_name='followed_playlists',
        blank=True,
        verbose_name=_("followers"),
        help_text=_("Users following this playlist. Followers cannot edit a playlist")
    )

    revibe_curated = models.BooleanField(
        null=False, blank=True, default=False,
        verbose_name=_("revibe curated"),
        help_text=_("Revibe-curated playlist. Must set 'is public' to True in order for this to be available")
    )
    show_on_browse = models.BooleanField(
        null=False, blank=True, default=False,
        verbose_name=_("show on browse"),
        help_text=_("Allow this playlist to display on the Browse page. If not checked, it will still be available in search or in a user's followed playlists")
    )

    date_created = models.DateField(
        auto_now_add=True, editable=False
    )

    class Meta:
        verbose_name = 'playlist'
        verbose_name_plural = 'playlists'

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return default_repr(self)


class LibrarySong(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE, null=False, related_name='library_to_song')
    song = models.ForeignKey('content.song', on_delete=models.CASCADE, null=False, related_name='song_to_library')

    date_saved = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'library song'
        verbose_name_plural = 'library songs'

    def __str__(self):
        return "{} in {}".format(self.song, self.library)

    def __repr__(self):
        return default_repr(self)


class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='playlist_to_song')
    song = models.ForeignKey('content.song', on_delete=models.CASCADE, related_name='song_to_playlist')

    date_saved = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'playlist song'
        verbose_name_plural = 'playlist songs'

    def __str__(self):
        return "{} in {}".format(self.song, self.playlist)

    def __repr__(self):
        return default_repr(self)

