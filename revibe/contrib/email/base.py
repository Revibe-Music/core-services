"""
Created: 5 Mar. 2020
Author: Jordan Prechac
"""

from django.template.loader import render_to_string

from revibe._helpers import const

# -----------------------------------------------------------------------------

class EmailConfiguration:

    _default_context = {
        "revibe_medium_image": const.REVIBE_MEDIUM_IMAGE,
        "youtube_image": const.YOUTUBE_IMAGE,
        "twitter_image": const.TWITTER_IMAGE,
        "facebook_image": const.FACEBOOK_IMAGE,
        "instagram_image": const.INSTAGRAM_IMAGE,
    }

    email_options = {
        # artist stuff
        'artist_invite':  'accounts/artist_invite_email',# general invite for artists
        'contribution': 'accounts/contribution_invite_email_white', # invite for contributions, white background
        'contribution_black': 'accounts/contribution_invite_email_black', # invite for contributions, black background

        # user management
        'forgot_password': 'accounts/forgot_password',
    }

    def __init__(self, user=None, recipients, *args, **kwargs):
        self.user = user
        self.recipients = recipients

        use_artist_name = kwargs.get("artist", False)
        self._default_context["name"] = self.user.artist.name if use_artist_name else self.user.username

    def configure_email(subject, *args, **kwargs):
        name = self.user.artist.name if self.use_artist_name else self.user.username

        html_message = render_to_string()
