from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from revibe.utils.classes import default_repr

# -----------------------------------------------------------------------------

class Pathway(models.Model):
    # core fields
    name = models.CharField(
        max_length=255,
        null=False, blank=False,
        verbose_name=_("name"),
        help_text=_("Human-readable name for the path")
    )

    ARTIST = 'artist'
    LISTENER = 'listener'
    _type_choices = (
        (ARTIST, 'Artist'),
        (LISTENER, 'Listener'),
    )
    type = models.CharField(
        max_length=100,
        choices=_type_choices,
        null=False, blank=False,
        verbose_name=_("type"),
        help_text=_("The user group that this pathway is designed for.")
    )
    default = models.BooleanField(
        null=False, blank=False, default=False,
        verbose_name=_("default"),
        help_text=_("Denotes if this path is a default path for this user group.")
    )
    users = models.ManyToManyField(
        to='accounts.CustomUser',
        related_name='cs_paths',
        limit_choices_to={"programmatic_account": False},
        blank=True,
        verbose_name=_("users"),
        help_text=_("Users that are likely to be interested in the services promoted on this path")
    )

    # progression
    beginner_quota = models.DecimalField(
        max_digits=3, decimal_places=2,
        null=True, blank=True,
        verbose_name=_("beginner quota")
    )
    intermediate_quota = models.DecimalField(
        max_digits=3, decimal_places=2,
        null=True, blank=True,
        verbose_name=_("intermediate quota")
    )
    advanced_quota = models.DecimalField(
        max_digits=3, decimal_places=2,
        null=True, blank=True,
        verbose_name=_("advanced quota")
    )
    special_quota = models.DecimalField(
        max_digits=3, decimal_places=2,
        null=True, blank=True,
        verbose_name=_("special quota")
    )
    other_quota = models.DecimalField(
        max_digits=3, decimal_places=2,
        null=True, blank=True,
        verbose_name=_("other quota")
    )

    # extras
    # active # doesn't make sense here
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_("description"),
        help_text=_("Human-readable description for the path")
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
        ordering = ['name']
        verbose_name = "path"
        verbose_name_plural = "paths"


class Action(models.Model):
    # core fields
    name = models.CharField(
        max_length=255,
        null=False, blank=False,
        verbose_name=_("name"),
        help_text=_("Human-readable name for this action")
    )
    pathways = models.ManyToManyField(
        to='customer_success.pathway',
        through='customer_success.PathwayAction',
        related_name='actions',
        blank=True,
        verbose_name=_("pathways"),
        help_text=_("Pathways in which this action is included")
    )

    # verification
    required_request_body_kwargs = models.TextField(
        null=False, blank=False, default="{}",
        verbose_name=_("request body kwargs"),
        help_text=_("Keyword arguments that must evaludate to True when checked against the request parameter arguments. Must use JSON encoding.")
    )
    required_request_params_kwargs = models.TextField(
        null=False, blank=False, default="{}",
        verbose_name=_("request param kwargs"),
        help_text=_("Keyword arguments that must evaluate to True when checked against the request parameter arguments. Must use JSON encoding.")
    )
    required_response_body_kwargs = models.TextField(
        null=False, blank=False, default="{}",
        verbose_name=_("response kwargs"),
        help_text=_("Keywork arguments that must evaluate to True when checked against the response body. Must use JSON encoding.")
    )

    # notification stuff
    event = models.ForeignKey(
        to='notifications.TemporalEvent',
        on_delete=models.SET_NULL,
        related_name='actions',
        null=True, blank=True,
        verbose_name=_("event"),
        help_text=_("Denote which notifications to look for when recording notification attribution")
    )
    extra_events = models.ManyToManyField(
        to='notifications.ExternalEvent',
        related_name='action_prompts',
        blank=True,
        verbose_name=_("extra events"),
        help_text=_("Additional, attribution-only events. These are External Events that prompt the user to perform this action.")
    )

    MINUTES = 'minutes'
    HOURS = 'hours'
    DAYS = 'days'
    _time_choices = (
        (MINUTES, 'Minute(s)'),
        (HOURS, 'Hour(s)'),
        (DAYS, 'Day(s)'),
    )
    interval_period = models.CharField(
        max_length=50,
        choices=_time_choices,
        null=True, blank=True,
        verbose_name=_("time period"),
        help_text=_("The type of period to use for time filtering")
    )
    number_of_period = models.IntegerField(
        null=False, blank=True, default=1,
        verbose_name=_("number of periods"),
        help_text=_("Number of interval periods to use for time filtering")
    )

    # recurrence
    RECURRENCE_DESCRIPTION = _("##### NOT IMPLEMENTED ##### Options to set this action as a recurring action. If 'recurring' is checked, the time period fields cannot be blank for the recurrence to work.")
    recurring = models.BooleanField(
        null=False, blank=False, default=False,
        verbose_name=_("recurring"),
        help_text=_("Marks the action as recurring. This action can notify the users after the users has performed the action")
    )
    _recur_time_choices = (
        (DAYS, 'Day(s)'),
    )
    recur_interval_period = models.CharField(
        max_length=50, 
        choices=_recur_time_choices,
        null=True, blank=True,
        verbose_name=_("time period"),
        help_text=_("The type of time period to use for recurrance")
    )
    recur_number_of_periods = models.IntegerField(
        null=True, blank=True,
        verbose_name=_("number of periods"),
        help_text=_("The number of interval periods to wait before resending this action's notification.")
    )

    # extras
    active = models.BooleanField(
        null=False, blank=True, default=True,
        verbose_name=_("active"),
        help_text=_("Enable/disable this action")
    )
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_("description"),
        help_text=_("Description of the action")
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
        ordering = ['name']
        verbose_name = "action"
        verbose_name_plural = "actions"


class PathwayAction(models.Model):
    # core fields
    pathway = models.ForeignKey(
        to='customer_success.pathway',
        on_delete=models.CASCADE,
        related_name='pathwayactions',
        null=False, blank=False,
        verbose_name=_("pathway"),
        help_text=_("The pathway this action is related to")
    )
    action = models.ForeignKey(
        to='customer_success.action',
        on_delete=models.CASCADE,
        related_name='pathwayactions',
        null=False, blank=False,
        verbose_name=_("action"),
        help_text=_("The action this pathway is related to")
    )

    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    SPECIAL = 'special'
    OTHER = 'other'
    _priority_choices = (
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED, 'Advanced'),
        (SPECIAL, 'Special'),
        (OTHER, 'Other'),
    )
    ranking = models.CharField(
        max_length=100,
        choices=_priority_choices,
        null=False, blank=False,
        verbose_name=_("ranking"),
        help_text=_("The group in which this action resides in this pathway")
    )
    allow_recurrence = models.BooleanField(
        null=False, blank=False, default=False,
        verbose_name=_("allow recurrence"),
        help_text=_("Allow action recurrence in this path")
    )

    # extras
    active = models.BooleanField(
        null=False, blank=True, default=True,
        verbose_name=_("active"),
        help_text=_("Enable/Disable this relationship")
    )
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_("description"),
        help_text=_("Human-readable description for this relationship")
    )
    date_created = models.DateTimeField(
        auto_now_add=True
    )
    last_changed = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.pathway} {self.action}"

    def __repr__(self):
        return default_repr(self)


class ActionTaken(models.Model):
    # core fields
    action = models.ForeignKey(
        to='customer_success.Action',
        on_delete=models.CASCADE,
        related_name='actions_taken',
        null=False, blank=False,
        verbose_name=_("action"),
        help_text=_('The action taken')
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='actions_taken',
        null=False, blank=False,
        verbose_name=_("user"),
        help_text=_("The user that did something")
    )
    notification = models.ForeignKey(
        to='notifications.Notification',
        on_delete=models.SET_NULL,
        related_name='actions_taken',
        null=True, blank=True,
        verbose_name=_("notification"),
        help_text=_("The notification that triggered the user to take the action")
    )

    # extras
    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.action} - {self.user}"

    def __repr__(self):
        return default_repr(self)

    class Meta:
        verbose_name = "action taken"
        verbose_name_plural = "actions taken"



