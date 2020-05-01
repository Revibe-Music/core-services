from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import datetime
from uuid import uuid1

from revibe._helpers import const
from revibe.utils import classes
from revibe.utils.language import text

from administration import managers

# -----------------------------------------------------------------------------

class ContactForm(models.Model):

    id = models.AutoField(
        primary_key=True
    )
    user = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    first_name = models.CharField(
        max_length=255,
        null=True, blank=True,
        help_text=_("First Name")
    )
    last_name = models.CharField(
        max_length=255,
        null=True, blank=True,
        help_text=_("Last Name")
    )
    email = models.CharField(
        max_length=255, 
        null=True, blank=True,
        help_text=_("Email")
    )
    subject = models.CharField(
        max_length=255, 
        null=True, blank=True,
        help_text=_("Contact form subject / type of request")
    )
    message = models.TextField(
        null=False, blank=False,
        help_text=_("Message")
    )

    # administrative fields
    resolved = models.BooleanField(
        help_text=_("Indicates if the request/issue has been resolved or not"),
        null=False, blank=False, default=False
    )
    assigned_to = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        limit_choices_to={'is_staff': True, "programmatic_account": False},
        related_name='contact_form_assignment',
        help_text=_("Revibe staff member it's assigned to"),
        verbose_name=_("staff member"),
        null=True, blank=True
    )
    date_created = models.DateTimeField(
        help_text=_("When the form was submitted"),
        auto_now_add=True, null=True
    )
    last_changed = models.DateTimeField("Last time the form was edited", auto_now=True, null=True)

    _message_limit = 50
    def __str__(self):
        if self.subject:
            return self.subject + " - " + str(self.id)
        elif self.message:
            return f"{self.message[:self._message_limit]}{'...' if len(self.message) > self._message_limit else ''} - {self.id}"
        return f"Form {self.id}"


class Campaign(models.Model):
    _user_text = "user"
    _artist_text = "artist"
    _both_text = "both"
    destination_choices = (
        (_user_text, 'Listener'),
        (_artist_text, 'Artist'),
        (_both_text, "Artists and Listeners"),
        ('other', 'Other'),
    )

    uri = models.CharField(max_length=255, null=False, blank=False, unique=True, default=uuid1)
    name = models.CharField(max_length=255, null=False, blank=False)
    budget = models.IntegerField(null=False, blank=False)
    spent = models.IntegerField(null=True, blank=True)
    destination = models.CharField(
        max_length=255,
        null=True, blank=True,
        choices=destination_choices,
        help_text=_("Target audience")
    )

    def __str__(self):
        return self.name
    
    def create_url(self):
        lookup = {
            self._user_text: const.LISTENER_SIGNUP_LINK,
            self._artist_text: const.ARTIST_SIGNUP_LINK,
        }
        params = f"?cid={self.uri}"
        url = lookup.get(str(self.destination), "")
        return url + params
    create_url.short_description = 'Custom URL'
    create_url.admin_sort_field = 'uri'

    def _budget(self):
        """
        Formats the 'budget' column as a currency
        """
        if self.budget != None:
            return '${:,.2f}'.format(self.budget)
        return None
    _budget.short_description = "budget"
    _budget.admin_sort_field = "budget"

    def _spent(self):
        """
        Formats the 'spent' column as a currency
        """
        if self.spent != None:
            return '${:,.2f}'.format(self.spent)
        return None
    _spent.short_description = "spent"
    _spent.admin_sort_field = "spent"


class YouTubeKey(models.Model):
    key = models.CharField(
        help_text=_("API Key"),
        max_length=255,
        null=False, blank=False, unique=True
    )
    point_budget = models.IntegerField(
        help_text=_("Number of points this API key is allotted"),
        null=False, blank=True, default=0
    )
    number_of_users = models.IntegerField(
        help_text=_("Estimated number of users using this key"),
        null=False, blank=True, default=0
    )

    last_date_broken = models.DateField(
        null=True, blank=True,
        help_text=_("The last date that this key ran dry"),
        verbose_name=_("Most recent date expired")
    )

    date_created = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def is_valid(self):
        """
        Will return false if the key has failed more than the failure threshold.
        """
        if self.last_date_broken == datetime.date.today():
            return False
        else:
            return True

    objects = managers.YouTubeKeyManager()

    def __str__(self):
        return str(self.key)

    class Meta:
        verbose_name = 'YouTube Key'
        verbose_name_plural = 'YouTube Keys'
        ordering = ['-point_budget']


class Alert(models.Model):

    _category_choices = (
        ("warn", "Warning"),
        ("error", "Error"),
        ("info", "Information"),
        ("feature", "New Feature"),
        ("event", "Event"),
    )

    subject = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("subject"),
        help_text=_("The subject of the message to send")
    )
    message = models.TextField(
        null=False, blank=False,
        verbose_name=_("Message"),
        help_text=_("The content of the alert to send to users.")
    )
    category = models.CharField(
        max_length=255,
        null=False, blank=False,
        choices=_category_choices,
        verbose_name=_("alert category"),
        help_text=_("The type of alert to send to users")
    )
    start_date = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("message start date"),
        help_text=_("The date to start sending the alert on")
    )
    end_date = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("message end date"),
        help_text=_("The date to stop sending the alert on")
    )
    enabled = models.BooleanField(
        null=False, blank=False, default=True,
        verbose_name=_("Message is enabled"),
        help_text=_("When set to off, will not be sent to any more users")
    )

    date_created = models.DateTimeField(
        auto_now_add=True
    )

    users_seen = models.ManyToManyField(
        to="accounts.customuser",
        related_name="alerts_seen",
        through="administration.AlertSeen",
        help_text=_("The users that have seen this alert")
    )

    # managers
    objects = models.Manager()
    display_objects = managers.AlertDisplayManager()

    def _get_subject(self):
        return self.subject if self.subject != None else "no subject"

    class Meta:
        verbose_name = "system alert"
        verbose_name_plural = "system alerts"

    def __str__(self):
        erythang = f"{self._get_subject()} - {self.message}"
        return text.truncate_string(erythang)


class AlertSeen(models.Model):

    alert = models.ForeignKey(
        to='administration.alert',
        on_delete=models.CASCADE,
        related_name="alert_seen",
        null=False, blank=False,
        verbose_name=_("alert"),
        help_text=_("Related system alert")
    )
    user = models.ForeignKey(
        to='accounts.customuser',
        on_delete=models.CASCADE,
        related_name="alert_seen",
        null=False, blank=False,
        verbose_name=_("user"),
        help_text=_("User that saw the alert")
    )

    has_seen = models.BooleanField(
        null=False, blank=True, default=True,
        verbose_name=_("has seen"),
        help_text=_("Indicates that the user has seen the alert")
    )

    class Meta:
        verbose_name = "alert seen"
        verbose_name_plural = "alerts seen"


class ArtistSpotlight(models.Model):

    date = models.DateField(
        primary_key=True
    )
    artist = models.ForeignKey(
        to='content.artist',
        on_delete=models.CASCADE,
        related_name='spotlights',
        limit_choices_to={'platform': const.REVIBE_STRING},
        null=False, blank=False,
        verbose_name=_("artist"),
        help_text=_("Artist to spotlight on the Revibe Music home screen")
    )

    def __str__(self):
        return f"{self.date} - {self.artist.name}"

    class Meta:
        verbose_name = "artist spotlight"
        verbose_name_plural = "artist spotlights"


class Blog(models.Model):

    display_style_choices = (
        (1, "Style A"),
        (2, "Style B"),
    )
    category_choices = (
        ('artist_of_the_week', 'Artist of the Week'),
        ('education', 'Education'),
        ('playlist', 'Playlist'),
        ('other', 'Other'),
    )

    category = models.CharField(
        max_length=255,
        choices=category_choices,
        null=False, blank=False,
        verbose_name=_("category"),
        help_text=_("Which blog this post belongs to")
    )
    title = models.CharField(
        max_length=255,
        null=False, blank=False,
        verbose_name=_("title"),
        help_text=_("Title of the post")
    )
    body = models.TextField(
        null=False, blank=False,
        verbose_name=_("body"),
        help_text=_("body of the post")
    )
    summary = models.TextField(
        null=True, blank=True,
        verbose_name=_("summary"),
        help_text=_("A quick summary of the post")
    )
    publish_date = models.DateField(
        default=datetime.date.today,
        verbose_name=_("publish date"),
        help_text=_("date that the post will go live")
    )
    header_image = models.FileField(
        null=True, blank=True,
        verbose_name=_("header image"),
        help_text=_("Image to be used at the top of the blog post")
    )
    side_image = models.FileField(
        null=False, blank=True,
        verbose_name=_("side image"),
        help_text=_("Image for the side of the blog post")
    )
    tags = models.ManyToManyField(
        to='administration.blogtag',
        related_name='blogs',
        blank=True,
        verbose_name=_("tags"),
        help_text=_("Associated tags")
    )

    author = models.ForeignKey(
        to='accounts.customuser',
        on_delete=models.SET_NULL,
        related_name='posted_blogs',
        limit_choices_to={'is_staff': True},
        null=True, blank=True,
        verbose_name=_("author"),
        help_text=_("The staff member who wrote the article")
    )
    artist = models.ForeignKey(
        to='content.artist',
        on_delete=models.SET_NULL,
        related_name='blogs_single',
        limit_choices_to={"platform": "Revibe"},
        null=True, blank=True,
        verbose_name=_("artist"),
        help_text=_("Artist related to the blog post, like an 'Artist of the Week'-type post.")
    )
    artists = models.ManyToManyField(
        to='content.artist',
        related_name='blogs_multiple',
        limit_choices_to={"platform": 'Revibe'},
        blank=True,
        verbose_name=_("artists"),
        help_text=_("Artists related to the blog post, like weekly featured artists or something like that.")
    )

    display_style = models.IntegerField(
        null=False, blank=True, default=1,
        choices=display_style_choices,
        verbose_name=_("display style"),
        help_text=_("Style to display the post in. See documentation for info")
    )

    date_created = models.DateTimeField(
        auto_now_add=True
    )

    objects = models.Manager()
    display_objects = managers.BlogDisplayManager()

    class Meta:
        verbose_name = "blog post"
        verbose_name_plural = "blog posts"

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.__str__()})>"


class BlogTag(models.Model):
    text = models.CharField(
        max_length=255,
        null=False, blank=False,
        verbose_name=_("text"),
        help_text=_("Text")
    )

    date_created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.text

    def __repr__(self):
        return classes.default_repr(self)
    
    class Meta:
        verbose_name = 'blog tag'
        verbose_name_plural = 'blog tags'


class Variable(models.Model):

    _category_choices = (
        ('artist-portal', 'Artist Portal Dashboard'),
        ('browse', 'Browse'),
        ('search', 'Search'),
        ('social', 'Social'),
        ('util', 'Utils'),
    )

    key = models.CharField(
        max_length=255,
        unique=True,
        null=False, blank=False,
        verbose_name=_("key"),
        help_text=_("key of the key-value pair")
    )
    value = models.TextField(
        null=False, blank=False,
        verbose_name=_("value"),
        help_text=_("value of the key-value pair")
    )
    rules = models.TextField(
        null=True, blank=True,
        verbose_name=_("variable rules"),
        help_text=_("Detail how to set up this value. Some variables require string formatting, such as 'mobile_app_share_text'.")
    )

    category = models.CharField(
        max_length=255,
        choices=_category_choices,
        null=True, blank=True,
        verbose_name=_("category"),
        help_text=_("Type of variable this is. Only used for sorting/filtering in the admin portal.")
    )

    class Meta:
        verbose_name = "variable"
        verbose_name_plural = "variables"

    def __str__(self):
        return self.key
    
    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.__str__()})>"

