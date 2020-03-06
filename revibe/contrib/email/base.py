"""
Created: 5 Mar. 2020
Author: Jordan Prechac
"""

from django.conf import settings
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
        "support_email": const.SUPPORT_EMAIL,
    }

    email_options = {
        # artist stuff
        'artist_invite':  { # general invite for artists
            _template: 'accounts/artist_invite_email',
            "subject": '{artist_name} has invited you to join Revibe!',
            "requirements": {"artist": True},
        },
        'contribution': { # invite for contributions, white background
            _template: 'accounts/contribution_invite_email_white',
            'subject': '{artist_name} has invited you to join Revibe!',
            "requirements": {"artist": True},
        },
        'contribution_black': { # invite for contributions, black background
            _template: 'accounts/contribution_invite_email_black',
            'subject': '{artist_name} has invited you to join Revibe!',
            "requirements": {"artist": True},
        },

        # user management
        'reset_password': { # forgot password
            _template: 'accounts/reset_password',
            'subject': 'Temporary Password',
        },
        'password_reset': {
            _template: 'accounts/password_reset', # password has been changed
            'subject': 'Your password has been changed',
        },
    }

    from_address = f'"Join Revibe" <{const.ARTIST_FROM_EMAIL}>'

    def __init__(self, user, recipients, template, subject=None, artist=False, fail_silently=True, *args, **kwargs):
        self.user = user
        self.recipients = recipients

        # kwargs
        self.use_artist = artist
        self.fail_silently = fail_silently
        self.temp_password = kwargs.get('temp_password', None)

        template = self._get_template(template)

    def _get_template(self, template_text):
        template = self.email_options.get(template_text, None)
        if template == None:
            raise network.BadRequestError("Could not identify the email template to use")
        
        requirements = template.get("requirements", None)
        if requirements != None:
            # check artist requirement
            if 'artist' in requirements.keys() and requirements['artist'] != self.use_artist:
                raise network.ProgramError(f"Sending Artist email, must include kwarg 'artist' when instantiating {self.__class__.__name__}")
        
        self.template = template

        # configure subject email
        self.subject = template.get('subject', "Revibe automated email service") # temp
        subject = template.get('subject', None)
        if subject != None:
            artist_name = self.user.artist.name if getattr(self.user, 'artist', None) != None else None
            subject = subject.format(artist_name=artist_name, username=self.user.username)

        return template

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
        context['temp_password'] = self.temp_password

        return context

    def configure_email(self, *args, **kwargs):
        html_message = render_to_string(self.template[_template], context=self.configure_context())
        return html_message

    def send_email(self, *args, **kwargs):

        # only send emails in the cloud
        if not settings.USE_S3:
            raise network.BadEnvironmentError("Cannot send emails outside of a cloud environment")

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

