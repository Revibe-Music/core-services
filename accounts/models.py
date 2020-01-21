from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
# from oauth2_provider.models import AccessToken, AbstractAccessToken

# -----------------------------------------------------------------------------


class CustomUser(AbstractUser):
    artist = models.OneToOneField('content.artist', on_delete=models.SET_NULL, related_name='artist_user', null=True, blank=True)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    is_artist = models.BooleanField(
        help_text='Flag that indicates this user has an Artist Profile',
        null=False, blank=True, default=False
    )
    is_manager = models.BooleanField(
        help_text='Flag that indicates this user is a manager of an artist', 
        null=False, blank=True, default=False
    )

class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    email = models.CharField(
        "User's email address",
        max_length=255, null=True, blank=True, unique=True
    )
    campaign = models.ForeignKey('administration.Campaign', on_delete=models.SET_NULL, null=True, blank=True, default=None)

    country = models.CharField(
        'Country',
        max_length=255, null=True, blank=True
    )
    dob = models.DateField(
        'Date of Birth',
        null=True, blank=True
    )
    image = models.FileField(
        "Profile Picture",
        upload_to='images/profiles', null=True, blank=True
    )

    # user settings fields
    allow_explicit = models.BooleanField(
        help_text="Allow the user to listen to explicit content",
        null=False, blank=True, default=True
    )
    skip_youtube_when_phone_is_locked = models.BooleanField(
        help_text="Skip YouTube content while phone is locked",
        null=False, blank=True, default=True
    )

    # privacy settings
    allow_listening_data = models.BooleanField(
        help_text="Allow this user to be linked to the recorded listening data",
        null=False, blank=True, default=True
    )

    # notification settings
    allow_email_marketing = models.BooleanField(
        help_text="Allow Revibe to send email to the user for marketing purposes",
        null=False, blank=True, default=True
    )

    def __str__(self):
        return "{}'s User Profile".format(self.user)

class ArtistProfile(models.Model):
    id = models.AutoField(primary_key=True)
    artist = models.OneToOneField('content.artist', on_delete=models.CASCADE, related_name='artist_profile', null=False, blank=False)

    # additional fields
    email = models.CharField(max_length=255, null=True, blank=True)
    about_me = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    zip_code = models.CharField(max_length=255, null=True, blank=True)

    # account settings
    require_contribution_approval = models.BooleanField(
        help_text="Require that all new contributions must be approved by the artist",
        null=False, blank=True, default=True
    )
    require_contribution_approval_on_edit = models.BooleanField(
        help_text="Require that all changes to contributions must be re-approved by the artist",
        null=False, blank=True, default=True
    )
    share_data_with_contributors = models.BooleanField(
        help_text="Allow streaming data to be shared with contributors to uploaded content",
        null=False, blank=True, default=True
    )
    share_advanced_data_with_contributors = models.BooleanField(
        help_text="Allow advanced streaming data to be shared with contributors to uploaded content",
        null=False, blank=True, default=False
    )
    allow_contributors_to_edit_contributions = models.BooleanField(
        help_text="Allow contributors to edit their contributions to content", # can delete contributions regardless
        null=False, blank=True, default=False
    )
    hide_all_content = models.BooleanField(
        help_text="Hide all artist's content from appearing in the Revibe app, and prevents the artist from being added as a contributor.",
        null=False, blank=True, default=False
    )
    display_other_platform_content_on_revibe_page = models.BooleanField(
        help_text="Display Spotify/YouTube content on the artist's Revibe artist page",
        null=False, blank=True, default=False
    )

    def __str__(self):
        return "{}'s Artist Profile".format(self.artist)

class Social(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='user_social')
    platform = models.CharField(max_length=255, null=True)


