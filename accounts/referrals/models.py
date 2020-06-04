from django.db import models
from django.utils.translation import gettext_lazy as _

from revibe.utils.classes import default_repr

# -----------------------------------------------------------------------------


class Referral(models.Model):

    referrer = models.ForeignKey(
        to='accounts.CustomUser',
        on_delete=models.SET_NULL,
        related_name='referalls',
        null=True, blank=False,
        verbose_name=_("sent"),
        help_text=_("The user that did the referring")
    )

    referree = models.OneToOneField(
        to='accounts.CustomUser',
        on_delete=models.SET_NULL,
        related_name='referral',
        null=True, blank=False,
        verbose_name=_("referred"),
        help_text=_("The user that was referred")
    )

    referree_ip_address = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("referred IP address"),
        help_text=_("The IP address of the referree. Used for scam prevention")
    )

    # extras
    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.referrer} - {self.referree}"

    def __repr__(self):
        return default_repr(self)

    class Meta:
        verbose_name = "referral"
        verbose_name_plural = "referrals"


class PointCategory(models.Model):
    name = models.CharField(
        max_length=255,
        null=False, blank=False, unique=True,
        verbose_name=_("name")
    )

    points = models.IntegerField(
        null=False, blank=False, default=0,
        verbose_name=_("points"),
        help_text=_("The number of points to be assigned for a referred user taking this action")
    )

    # configuration
    repeating = models.BooleanField(
        null=False, blank=False, default=False,
        verbose_name=_("repeating"),
        help_text=_("Allow referring users to receive points for an action multiple times")
    )

    DAYS = 'days'
    _expiration_interval_choices = (
        (DAYS, 'Days'),
    )
    expiration_interval = models.CharField(
        max_length=100,
        choices=_expiration_interval_choices,
        null=True, blank=True,
        verbose_name=_("expiration interval"),
        help_text=_("Time period to use when expiring, time is compared to the time of the user's registration. Leave blank to not expire")
    )
    expiration_number_of_periods = models.IntegerField(
        null=True, blank=True,
        verbose_name=_("number of periods"),
        help_text=_("Number of expiration periods")
    )

    # extras
    active = models.BooleanField(
        null=False, blank=False, default=True,
        verbose_name=_("active"),
        help_text=_("This category will be used to assign points to users")
    )
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_("description"),
        help_text=_("Human-readable information about this category")
    )

    date_created = models.DateTimeField(
        auto_now_add=True
    )
    last_changed = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return default_repr(self)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"


class Point(models.Model):
    referral = models.ForeignKey(
        to='Referral',
        on_delete=models.SET_NULL,
        related_name="points",
        null=True, blank=False,
        verbose_name=_("referral")
    )
    category = models.ForeignKey(
        to='PointCategory',
        on_delete=models.SET_NULL,
        related_name=_("assigned_points"),
        null=True, blank=False,
        verbose_name=_("category")
    )

    points = models.IntegerField(
        null=False, blank=False,
        verbose_name=_("points"),
        help_text=_("The change in points for this user")
    )

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        if self.category and self.referral:
            return f"{self.referral} - {self.category}"
        return f"-no user ({self.id})-"

    def __repr__(self):
        return default_repr(self)

    class Meta:
        verbose_name = "point"
        verbose_name_plural = "points"



