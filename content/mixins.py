# version mixins
class V1Mixin:
    def get_version(**kwargs):
        kwargs['version'] = 'v1'
        return kwargs

class V2Mixin:
    def get_version(**kwargs):
        kwargs['version'] = 'v2'
        return kwargs


class ContributionSerializerMixin:
    def get_account_settings(self, artist, *args, **kwargs):
        if hasattr(artist, 'artist_profile'):
            artist_profile = artist.artist_profile
            pending = True if artist_profile.require_contribution_approval else False
            approved = not pending
            return {
                "pending": pending,
                "approved": approved
            }
        else:
            return None
