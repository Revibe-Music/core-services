from revibe._errors.accounts import ProfileNotFoundError

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
    def get_account_settings(self, artist, create=False, update=False, *args, **kwargs):
        """
        """
        assert not (create and update), "cannot both update and create in 'get_account_settings'."
        if not hasattr(artist, 'artist_profile'):
            raise ProfileNotFoundError("Could not identify the current profile")

        artist_profile = artist.artist_profile
        # defaults
        pending = True
        approved = not pending

        if create:
            # if creating the contribution...
            pending = True if artist_profile.require_contribution_approval else False
            approved = not pending
        elif update:
            # if updating the contribution...
            pending = True if artist_profile.require_contribution_approval_on_edit else False
            approved = not pending
        
        else:
            # if 'create' and 'update' are both not sent, then just send the profile
            return artist_profile

        return {
            "pending": pending,
            "approved": approved
        }

