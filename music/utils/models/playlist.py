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

            remove_kwargs = ['platform', 'song', 'artist', 'album']
            valid_data = song
            for kwarg in remove_kwargs:
                valid_data.pop(kwarg, None)

            ps = PlaylistSong.objects.create(playlist=playlist, song=song_object, **valid_data)
            ps.save()

            songs_added += 1
        except Exception as e:
            print(e)
            failures += 1

            if hasattr(song, 'song'):
                song_id = song.get('song').get('song_id')
            else:
                song_id = song['song_id']

            details = {"id": song_id, "detail": str(e)}
            failure_details.append(details)

    return {"songs_added": songs_added, "failures": failures, "details": failure_details}

