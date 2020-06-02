from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from revibe.utils.classes import default_repr

from .utils.models import custom_file_upload

# -----------------------------------------------------------------------------


class ArtistOfTheWeek(models.Model):
    user = models.ForeignKey(
        to='accounts.CustomUser',
        on_delete=models.SET_NULL,
        related_name='artistoftheweek_applications',
        limit_choices_to=(Q(is_artist=True) | Q(artist__isnull=False)),
        null=True, blank=True,
        verbose_name=_("user"),
        help_text=_("The user that submitted the application")
    )

    promotion_ideas = models.TextField(
        null=True, blank=True,
        verbose_name=_("promotion ideas")
    )
    picture = models.FileField(
        upload_to=custom_file_upload,
        null=True, blank=True,
        verbose_name=_("picture")
    )

    # social media links n stuff
    facebook_link = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("Facebook link")
    )
    instagram_handle = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("Instagram handle")
    )
    soundcloud_link = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("Soundcloud link")
    )
    spotify_link = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("Spotify link")
    )
    youtube_link = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("Youtube link")
    )

    other_link_description_1 = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("other link description 1")
    )
    other_link_1 = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("other link 1")
    )
    other_link_description_2 = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("other link description 2")
    )
    other_link_2 = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("other link 2")
    )
    other_link_description_3 = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("other link description 3")
    )
    other_link_3 = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("other link 3")
    )

    # staff info
    seen = models.BooleanField(
        null=False, blank=False, default=False,
        verbose_name=_("seen"),
        help_text=_("Mark if the application has been seen by a member of the Revibe team.")
    )

    PENDING = 'pending'
    APPROVED = 'approved'
    DENIED = 'denied'
    COMPLETE = 'complete'
    _status_choices = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (DENIED, 'Denied'),
        (COMPLETE, 'Completed')
    )
    status = models.CharField(
        max_length=50,
        choices=_status_choices,
        null=False, blank=False, default=PENDING,
        verbose_name=_("status"),
        help_text=_("Application status")
    )
    post = models.ForeignKey(
        to='administration.blog',
        on_delete=models.SET_NULL,
        related_name='application',
        limit_choices_to={"category": "artist_of_the_week"},
        null=True, blank=True,
        verbose_name=_("blog post"),
        help_text=_("The blog post that was written from this application")
    )

    staff_notes = models.TextField(
        null=True, blank=True,
        verbose_name=_("staff notes")
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
        null=True
    )
    last_changed = models.DateTimeField(
        auto_now=True,
        null=True
    )


    def __str__(self):
        name = self.user.artist.name if getattr(self.user, 'artist', None) else self.user.username
        return f"{name} ({self.id})"

    def __repr__(self):
        return default_repr(self)

    class Meta:
        verbose_name = "artist of the week"
        verbose_name_plural = "artists of the week"




