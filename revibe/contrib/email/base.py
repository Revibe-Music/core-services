"""
Created: 5 Mar. 2020
Author: Jordan Prechac
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from revibe._errors import network
from revibe._helpers import const

# -----------------------------------------------------------------------------

_template = "template" # defining the string to avoid typos

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
        'artist_invite':  { # general invite for artists
            _template: 'accounts/artist_invite_email',
            # "subject": ''
            "requirements": {"artist": True},
        },
        'contribution': { # invite for contributions, white background
            _template: 'accounts/contribution_invite_email_white',
            "requirements": {"artist": True},
        },
        'contribution_black': { # invite for contributions, black background
            _template: 'accounts/contribution_invite_email_black',
            "requirements": {"artist": True},
        },

        # user management
        'forgot_password': {
            _template: 'accounts/forgot_password',
            'subject': 'Temporary Password',
        },
        'password_reset': {
            _template: 'accounts/password_reset',
            'subject': 'Your password has been changed',
        },
    }

    from_address = f'"Join Revibe" <{const.ARTIST_FROM_EMAIL}>'

    def __init__(self, user=None, recipients, template, subject=None, *args, **kwargs):
        self.user = user
        self.recipients = recipients
        self.use_artist = kwargs.get("artist", False)

        template = self.email_options.get(template, None)
        if template == None:
            raise network.BadRequestError("Could not identify the email template to use")
        self.template = template
        self.subject = subject if subject != None else template.get('subject', None)

    def get_register_link(self, *args, **kwargs):
        link = "https://artist.revibe.tech/account/register" if self.use_artist else "https://revibe.tech"
        url_params = {
            "uid": str(self.user.id) if self.user else ""
        }
        url_param_string = "&".join([f"{param}={value}" for param, value in url_params.items()])

        return f"{link}?{url_param_string}"

    def configure_context(self, *args, **kwargs):
        context = self._default_context

        context['register_link'] = self.get_register_link()
        context["name"] = self.user.artist.name if self.use_artist else self.user.username

        return context

    def configure_email(self, *args, **kwargs):
        name = self.user.artist.name if self.use_artist else self.user.username

        html_message = render_to_string(self.template, context=self.configure_context())

    def send_email(self, subject, fail_silently=True, *args, **kwargs):
        html_message = self.configure_email()
        plain_message = strip_tags(html_message)

        num_sent = 0
        for rec in self.recipients:
            num_sent += send_mail(
                subject=self.subject,
                message=plain_message,
                from_email=self.from_address,
                recipient_list=[rec,],
                html_message=html_message,
                fail_silently=fail_silently
            )

        return num_sent

