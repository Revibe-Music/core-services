"""
Created: 07 May 2020
Author: Jordan Prechac
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

import datetime

from revibe.utils.classes import default_repr

# -----------------------------------------------------------------------------

class Event(models.Model):
    # relationships

    # core fields
    name = models.CharField(
        max_length=255,
        null=False, blank=False, unique=True,
        verbose_name=_("name"),
        help_text=_("Identifying name of the event")
    )
    trigger = models.CharField(
        max_length=255,
        null=False, blank=False,
        verbose_name=_("trigger"),
        help_text=_("Action that triggers the notification to be sent")
    )
    trigger_delay = models.DurationField(
        null=True, blank=True,
        verbose_name=_("trigger delay"),
        help_text=_("Time delay on sending the notification after the trigger is activated. Use the format '[DD] [[hh:]mm:]ss'.")
    )
    desired_action = models.CharField(
        max_length=255,
        null=False, blank=False,
        verbose_name=_("desired action"),
        help_text=_("Action the user is desired to take after receiving this notification")
    )

    # extras
    active = models.BooleanField(
        null=False, blank=True, default=True,
        verbose_name=_("active"),
        help_text=_("The event is active and will send notifications. Please set this to False rather than deleting the object; deleting the object will inhibit analysis.")
    )
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_("description"),
        help_text=_("Description of the event")
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
        verbose_name = "event"
        verbose_name_plural = "events"


class Reminder(models.Model):
    # relationships
    # success_action = models.ForeignKey()

    # core fields
    name = models.CharField(
        max_length=255,
        null=False, blank=False, unique=True,
        verbose_name=_("name"),
        help_text=_("Name of the reminder")
    )
    desired_action = models.CharField(
        max_length=255,
        null=False, blank=False,
        verbose_name=_("desired action"),
        help_text=_("ACtion the user is desired to take after receiving this reminder")
    )
    automation_order = models.IntegerField(
        null=True, blank=True, unique=True,
        verbose_name=_("automation order"),
        help_text=_("Order in the automation stack that this reminder will be executed")
    )
    for_artists = models.BooleanField(
        null=False, blank=False,
        verbose_name=_("for artists"),
        help_text=_("This notification is for artists, not listeners.")
    )

    # extras
    active = models.BooleanField(
        null=False, blank=True, default=True,
        verbose_name=_("active"),
        help_text=_("The reminder is active and will send notifications. Please set this to False rather than deleting the object; deleting the object will inhibit analysis.")
    )
    description = models.TextField(
        null=False, blank=False,
        verbose_name=_("description"),
        help_text=_("Text explanation of the reminder")
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
        verbose_name = "reminder"
        verbose_name_plural = "reminders"


class NotificationTemplate(models.Model):
    # relationships
    event = models.ForeignKey(
        to='notifications.Event',
        on_delete=models.SET_NULL,
        related_name="templates",
        null=True, blank=True,
        verbose_name=_("event"),
        help_text=_("Event to use this as a notification for. If set to Null, this template will not be able to be used.")
    )

    # core fields
    # notification_method = models.
    text_template = models.TextField(
        null=False, blank=False,
        verbose_name=_("text template"),
        help_text=_("The core text template of the notification. This is all that will be sent unless using email notifications, in which case this will the main text of the email in the email template.")
    )
    html = models.TextField(
        null=True, blank=True,
        verbose_name=_("HTML template"),
        help_text=_("The HTML template to send as the email. If not sending email notification, the template will not be used. See the documentation for proper configuration of notification HTML templates.")
    )

    # extras
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_("description"),
        help_text=_("Description of the template")
    )
    date_created = models.DateTimeField(
        auto_now_add=True
    )
    last_changed = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.event.__str__()} ({self.id})"

    def __repr__(self):
        return default_repr(self)

    class Meta:
        verbose_name = "notification template"
        verbose_name_plural = "notification templates"


class Notification(models.Model):
    # relationships
    event_template = models.ForeignKey(
        to='notifications.NotificationTemplate',
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True, blank=False,
        verbose_name=_("event template"),
        help_text=_("The the event template that sent this notification")
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True, blank=True,
        verbose_name=_("user"),
        help_text=_("The user that was sent the notification")
    )

    # core fields
    is_artist = models.BooleanField(
        null=False, blank=True, default=False,
        verbose_name=_("is artist"),
        help_text=_("The event is an artist notification, not a user notification")
    )
    action_taken = models.BooleanField(
        null=True, blank=True, default=None,
        verbose_name=_("action taken"),
        help_text=_("The action has been taken by the user. Treat it like False if it's been 'x' days since the notification was sent")
    )
    date_of_action = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("date of action"),
        help_text=_("Date & time the desired action was taken")
    )

    # extras
    date_created = models.DateTimeField(
        auto_now_add=True
    )
    last_changed = models.DateField(
        auto_now=True
    )

    def __str__(self):
        if self.event_template != None and self.event_template.event != None and self.user != None:
            return f"{self.user.__str__()} ({self.event_template.event.__str__()})"
        else:
            return super().__str__()

    def __repr__(self):
        return default_repr(self)

    class Meta:
        verbose_name = "notification"
        verbose_name_plural = "notifications"

