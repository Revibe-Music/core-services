"""
Created: 18 Mar. 2020
Author: Jordan Prechac
"""

from content.models import PlaceholderContribution, SongContributor, AlbumContributor

# -----------------------------------------------------------------------------

def create_permananent_contribs(artist):
    """
    Will take an artist's email, find all the placeholder contributions with 
    that email, and convert them to actual contributions.

    Arguments
    ---------
    artist: (<content.Artist>) the artist to move placeholders to

    Examples
    --------
    """
    email = str(artist.artist_user.profile.email)

    placeholders = PlaceholderContribution.objects.filter(email=email)

    if placeholders.count() == 0:
        return
    
    song_placeholders = placeholders.filter(song__isnull=False)
    album_placeholders = placeholders.filter(album__isnull=False)

    for song_contrib in song_placeholders:
        # create the song contribution
        new_contrib = SongContributor.objects.create(
            artist=artist,
            song=song_contrib.song,
            contribution_type=song_contrib.contribution_type,
            primary_artist=False,
            pending=True, approved=False
        )
        new_contrib.save()

        # delete the placeholder
        song_contrib.delete()
    
    for album_contrib in album_placeholders:
        # create the album contribution
        new_contrib = AlbumContributor.objects.create(
            artist=artist, 
            album=album_contrib.album,
            contribution_type=album_contrib.contribution_type,
            primary_artist=False,
            pending=True, approved=False
        )

        # delete the placeholder
        album_contrib.delete()

    return
