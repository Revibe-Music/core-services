"""
Created: 25 Mar. 2020
Author: Jordan Prechac
"""

from revibe.platforms import get_platform

from music.models import Playlist, PlaylistSong

# -----------------------------------------------------------------------------

def bulk_add_songs_to_playlist(playlist_id, songs, *args, **kwargs):
    """
    """

    playlist = Playlist.objects.get(id=playlist_id)

    songs_added = 0
    failures = 0
    failure_details = []

    for song in songs:
        try:
            platform = get_platform(song.get('platform', 'revibe'))
            song_object = platform.save(song)

            ps = PlaylistSong.objects.create(playlist=playlist, song=song_object)
            ps.save()

            songs_added += 1
        except Exception as e:
            failures += 1
            failure_details.append(str(e))

    return {"songs_added": songs_added, "failures": failures, "details": failure_details}

