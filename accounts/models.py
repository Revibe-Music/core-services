from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager, UserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from revibe.utils.classes import default_repr

from . import managers

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

    force_change_password = models.BooleanField(
        null=False, blank=True, default=False,
        verbose_name=_("force change password"),
        help_text=_("User must change password on login")
    )

    log_in_mobile_app = models.BooleanField(
        null=False, blank=True, default=False,
        verbose_name=_("logged in to Revibe Music mobile"),
        help_text=_("Indicates if the user has logged in to the mobile app before")
    )
    log_in_artist_portal = models.BooleanField(
        null=False, blank=True, default=False,
        verbose_name=_("logged in to Revibe Artist Portal"),
        help_text=_("Indicates if the user has logged in to the artist portal before/")
    )

    programmatic_account = models.BooleanField(
        null=True, blank=True, default=False,
        verbose_name=_("programmatic account"),
        help_text=_("Programmatic accounts cannot login by normal means, they can only have access token generated for use in supplemental applications")
    )
    temporary_account = models.BooleanField(
        null=False, blank=True, default=False,
        verbose_name=_("temporary account"),
        help_text=_("Temporary accounts are people who have downloaded the app but have not yet fully registered for an account.")
    )
    date_registered = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("date registered"),
        help_text=_("The datetime the user claimed their account")
    )

    friends = models.ManyToManyField(
        to='accounts.customuser',
        through='accounts.friendship',
        symmetrical=False,
        related_name='related_to+',
        blank=True,
        verbose_name=_("friends"),
        help_text=_("User's friends")
    )

    # def _get_link_url

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else ""

    def _link_to_self(self):
        return format_html(
            "<a href='/{}accounts/customuser/{}'>{}</a>",
            settings.ADMIN_PATH,
            self.id,
            self.__str__()
        )
    
    objects = UserManager()
    registered_objects = managers.RegisteredUserManager()


class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    email = models.CharField(
        help_text=_("User's email address"),
        max_length=255,
        null=True, blank=True, unique=True
    )
    campaign = models.ForeignKey(
        'administration.Campaign',
        on_delete=models.SET_NULL,
        help_text=_("The marketing campaign that got this user"),
        verbose_name="marketing campaign",
        null=True, blank=True, default=None
    )
    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="referred_users",
        help_text=_("The user that referred this one"),
        verbose_name=_("referrer"),
        null=True, blank=True, default=None
    )

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
    allow_search_data = models.BooleanField(
        null=False, blank=True, default=True,
        verbose_name=_("allow search data"),
        help_text=_("Allow this user to be linked the recorded search data")
    )
    allow_donation_data = models.BooleanField(
        null=False, blank=True, default=True,
        verbose_name=_("allow recording donation data"),
        help_text=_("Determines if the user's donations will be recorded with their user")
    )

    # notification settings
    allow_email_marketing = models.BooleanField(
        help_text="Allow Revibe to send email to the user for marketing purposes",
        null=False, blank=True, default=True
    )
    allow_email_notifications = models.BooleanField(
        null=False, blank=True, default=True,
        verbose_name=_("allow email notifications"),
        help_text=_("Allow notifications to be sent by email")
    )
    allow_email_reminders = models.BooleanField(
        null=False, blank=True, default=True,
        verbose_name=_("allow email reminders"),
        help_text=_("Allow reminders sent by email")
    )
    allow_sms_notifications = models.BooleanField(
        null=False, blank=True, default=True,
        verbose_name=_("allow sms notifications"),
        help_text=_("Allow notifications to be sent by sms")
    )
    allow_push_notifications = models.BooleanField(
        null=False, blank=True, default=True,
        verbose_name=_("allow pushy notifications"),
        help_text=_("Allow push notifications to be sent to the user's device")
    )
    allow_in_app_notifications = models.BooleanField(
        null=False, blank=True, default=True,
        verbose_name=_("allow in-app notifications"),
        help_text=_("Allow notifications to be sent in Revibe applications")
    )

    # new notification stuff:
    """
    Master 'Off Switch'??

    Split Listener & Artist notifications...

    Emails:
        all emails - master 'Off Switch'
        types:
            newletters
            transactional
            suggestions (customer success)
            promotional - just marketing stuff
            recap

    Push:
        all push - master 'Off Switch'
        types:
            transactional
            suggestions
            promotional
            follows (ex. artist I follow uploads a new song)

    In-App:
        all in-app
        types:
            transactional
            suggestions
            promotional
            follows (ex. artist I follow uploads a new song)

    Text:
        all text
        types:
            transactional
            suggestions
            promotional

    """

    def _link_to_self(self):
        return format_html(
            "<a href='/{}/accounts/profile/{}'>{}</a>",
            settings.ADMIN_PATH,
            self.id,
            self.__str__()
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
    public_url = models.CharField(
        max_length=100,
        null=True, blank=True,
        unique=True,
        verbose_name=_("public url"),
        help_text=_("The url string to this artist's page in Revibe.tech")
    )

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
        help_text="Allow contributors to edit their contributions to content",
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
    allow_contributors_to_edit_tags = models.BooleanField(
        help_text=_("Allows contributors to content to add/remove tags from that content"),
        null=False, blank=True, default=False
    )
    allow_revibe_website_page = models.BooleanField(
        null=False, blank=True, default=False,
        verbose_name=_("allow revibe website page"),
        help_text=_("Determines if the artist has a publicly available page on Revibe.tech")
    )

    def relink_url(self):
        return self.public_url if self.public_url != None else self.artist.id

    def __str__(self):
        return "{}'s Artist Profile".format(self.artist)


class StaffProfile(models.Model):
    # relationships
    _user_choices = {"is_staff": True, "programmatic_account": False, "temporary_account": False}
    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile",
        limit_choices_to=_user_choices,
        null=False, blank=False,
        verbose_name=_("user"),
        help_text=_("User account")
    )
    supervisor = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name=_("reports"),
        limit_choices_to=_user_choices,
        null=True, blank=True,
        verbose_name=_("supervisor"),
        help_text=_("Staff member's supervisor")
    )

    # job information
    job_title = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("job title"),
        help_text=_("Staff's job title")
    )
    display_name = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("display name"),
        help_text=_("Staff display name. Used for things like blog posts")
    )

    # pay information
    _pay_type_choices = (
        ("salary", "Salary"),
        ("wage", "Hourly Wage"),
    )
    pay_type = models.CharField(
        max_length=20,
        choices=_pay_type_choices,
        null=True, blank=True,
        verbose_name=_("pay type"),
        help_text=_("How the staff member is paid")
    )
    pay = models.DecimalField(
        max_digits=11, decimal_places=2,
        null=True, blank=True,
        verbose_name=_("pay"),
        help_text=_("How much the staff member is paid, either hourly or yearly")
    )


    # date information
    start_date = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("start date"),
        help_text=_("Staff's start date at Revibe")
    )
    job_start_date = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("job start date"),
        help_text=_("Date staff member started their current role")
    )

    def __str__(self):
        return self.display_name if self.display_name else (self.user.full_name if self.user.full_name != "" else self.user.__str__())
    
    def __repr__(self):
        return default_repr(self)
    
    class Meta:
        verbose_name = "staff account"
        verbose_name_plural = "staff accounts"


class Social(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='user_social')
    platform = models.CharField(max_length=255, null=True)


class SocialMedia(models.Model):
    _facebook_text = "facebook"
    _instagram_text = "instagram"
    _twitter_text = "twitter"

    _spotify_text = "spotify"
    _apple_music_text = "applemusic"
    _amazon_music_text = "amazonmusic"
    _youtube_text = "youtube"
    _soundcloud_text = "soundcloud"
    _tidal_text = "tidal"
    _google_play_music_text = "googleplaymusic"

    _venmo_text = "venmo"
    _cashapp_text = "cashapp"

    _other_text = "other"

    service_choices = (
        # social media
        (_facebook_text, "Facebook"),
        (_instagram_text, "Instagram"),
        (_twitter_text, "Twitter"),

        # music
        (_spotify_text, "Spotify"),
        (_apple_music_text, "Apple Music"),
        (_amazon_music_text, "Amazon Music"),
        (_youtube_text, "YouTube"),
        (_soundcloud_text, "SoundCloud"),
        (_tidal_text, "Tidal"),
        (_google_play_music_text, "Google Play Music"),

        # payment
        (_venmo_text, "Venmo"),
        (_cashapp_text, "Cash App"),

        (_other_text, "Other"),
    )


    artist_profile = models.ForeignKey(
        'accounts.ArtistProfile',
        on_delete=models.CASCADE,
        related_name="social_media",
        null=False, blank=False,
        help_text=_("Account's artist")
    )
    service = models.CharField(
        max_length=255,
        null=False, blank=False, default=_other_text,
        choices=service_choices,
        help_text=_("Social media service - Twitter, Instagram, etc.")
    )
    description = models.CharField(
        max_length=255,
        null=True, blank=True,
        help_text=_("If service is other, this will be the displayed value for the link")
    )
    handle = models.CharField(
        max_length=255,
        null=False, blank=False,
        help_text=_("Social media handle or URL")
    )

    order = models.IntegerField(
        null=True, blank=True,
        verbose_name=_("order"),
        help_text=_("The order to display the links in, if any")
    )

    def __str__(self):
        return f"{self._get_service()} - {self.handle}"

    def _get_service(self):
        return self.service if self.service != self._other_text else self.description

    def _generate_html_link(self):
        return format_html(
            "<a herf='{}' target='_blank'>{}</a>",
            self.handle,
            self._get_service()
        )
    _generate_html_link.short_description = "link to page"

    # _get_service.short_description = "Social Media"


class Friendship(models.Model):
    first = models.ForeignKey(
        to='accounts.customuser',
        on_delete=models.CASCADE,
        related_name='friends_first',
        limit_choices_to={"programmatic_account": False},
        null=False, blank=False,
        verbose_name=_("first"),
        help_text=_("First user, the one that instigated the friendship")
    )
    second = models.ForeignKey(
        to='accounts.customuser',
        on_delete=models.CASCADE,
        related_name='friends_second',
        limit_choices_to={"programmatic_account": False},
        null=False, blank=False,
        verbose_name=_("second"),
        help_text=_("Second user")
    )

    accepted = models.BooleanField(
        null=False, blank=True, default=False,
        verbose_name=_("accepted status"),
        help_text=_("Whether or not the friend request has been accepted")
    )

    created = models.DateTimeField(
        auto_now_add=True
    )
    updated = models.DateTimeField(
        auto_now=True
    )
    accepted_datetime = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("accepted datetime"),
        help_text=_("The date & time the request was accepted")
    )

    def __repr__(self):
        return default_repr(self)
    
    class Meta:
        verbose_name = "friendship"
        verbose_name_plural = "friendships"


