from logging import getLogger
logger = getLogger(__name__)

from revibe._errors.accounts import AccountNotFound, NotArtistError

# -----------------------------------------------------------------------------

def get_authenticated_artist(request):
    # check that the request has a user
    if not request.user:
        raise AccountNotFound() # 401

    # check that the user has an artist account
    if not request.user.artist:
        raise NotArtistError() # 403

    # double check that the artist has an artist profile
    artist = request.user.artist
    if not artist.artist_profile:
        artist_profile = ArtistProfile.objects.create(artist=artist)
        artist_profile.save()

    return artist

