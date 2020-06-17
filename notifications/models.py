"""
Created: 07 May 2020
Author: Jordan Prechac
"""

from django.conf import settings
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import datetime
import json
import uuid

from revibe.utils.classes import default_repr

from . import managers

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

    TEMPORAL = 'temporal'
    EXTERNAL = 'external'
    _type_choices = (
        (EXTERNAL, 'External'),
        (TEMPORAL, 'Temporal'),
    )
    type = models.CharField(
        max_length=100,
        choices=_type_choices,
        null=False, blank=False, default=EXTERNAL,
        verbose_name=_("type"),
        help_text=_("The type of Event this is")
    )

    trigger = models.CharField(
        max_length=255,
        null=False, blank=False,
        verbose_name=_("trigger"),
        help_text=_("Action that triggers the notification to be sent")
    )
    sent_address = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("sent address"),
        help_text=_("Email address the message is sent from. If ANY templates of this event use email notifications, this field CANNOT be blank!")
    )

    # verification
    required_request_headers = models.TextField(
        null=False, blank=False, default="{}",
        verbose_name=_("request headers"),
        help_text=_("Keyward arguments that must evaluate to True when checked against the request headers")
    )
    required_request_body = models.TextField(
        null=False, blank=False, default="{}",
        verbose_name=_("request body"),
        help_text=_("Keyward arguments that must evaluate to True when checked against the request body")
    )
    required_request_params = models.TextField(
        null=False, blank=False, default="{}",
        verbose_name=_("request params"),
        help_text=_("Keyward arguments that must evaluate to True when checked against the request parameters")
    )
    required_response_body = models.TextField(
        null=False, blank=False, default="{}",
        verbose_name=_("response body"),
        help_text=_("Keyward arguments that must evaluate to True when checked against the response body")
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

    def _link_to_self(self):
        return format_html(
            "<a href='/{}notifications/event/{}'>{}</a>",
            settings.ADMIN_PATH,
            self.id,
            self.__str__()
        )

    # model stuff
    objects = managers.EventManager()
    active_objects = managers.ActiveEventManager()

    def __str__(self):
        return self.name + f" ({self.type.capitalize()})"

    def __repr__(self):
        return default_repr(self)

    class Meta:
        verbose_name = "event"
        verbose_name_plural = "events"


class ExternalEvent(Event):
    objects = managers.ExternalEventManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('type').default = self.EXTERNAL
        super().__init__(*args, **kwargs)

    class Meta:
        proxy = True


class TemporalEvent(Event):
    objects = managers.TemporalEventManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('type').default = self.TEMPORAL
        super().__init__(*args, **kwargs)

    class Meta:
        proxy = True


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
    _medium_choices = (
        ('email', 'Email'),
        ('in_app', 'In-App'),
        ('push', 'Push'),
        ('sms', 'Text Message'),
    )
    medium = models.CharField(
        max_length=255,
        choices=_medium_choices,
        null=False, blank=False, 
        verbose_name=_("medium"),
        help_text=_("The medium by which to send the notification")
    )
    subject = models.TextField(
        null=True, blank=True,
        verbose_name=_("subject"),
        help_text=_("Notification subject. If sending an email message this field CANNOT be blank!")
    )
    body = models.TextField(
        null=False, blank=False,
        verbose_name=_("body"),
        help_text=_("The format-string message to send to the user. If this is an email template, paste the HTML here.")
    )

    # branch stuff
    # channel : use event type, have override field TODO
    branch_channel = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("channel"),
        help_text=_("Branch channel/source. Defaults to the Event's type (External/Temporal).")
    )
    # feature: use 'medium' field, no field
    # campaigns: use Event name, have an override field TODO
    branch_campaign = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("campaign"),
        help_text=_("Branch campaign field. Defaults to Event's 'name' field.")
    )
    # tags: comma-separated values. Gonna have to parse that out into a list later
    branch_tags = models.TextField(
        null=True, blank=True,
        verbose_name=_("tags"),
        help_text=_("Comma-separated tags for branch links. Will be null if left blank.")
    )

    # extras
    active = models.BooleanField(
        null=False, blank=True, default=True,
        verbose_name=_("active"),
        help_text=_("The template is active and will be used for notifications")
    )
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
        verbose_name = "template"
        verbose_name_plural = "templates"


    # branch stuff
    def get_branch_channel(self):
        channel = self.branch_channel if self.branch_channel else self.event.type
        return channel.lower()

    def get_branch_campaign(self):
        campaign = self.branch_campaign if self.branch_campaign else self.event.name
        return campaign.lower()

    def tags_to_list(self):
        tags_text = self.branch_tags

        # if the field is empty, return None
        if tags_text in [None, "", " ", "[]"]: return None

        try:
            # check if the tags have been input as a JSON-serialized list
            return json.loads(tags_text)
        except json.JSONDecodeError:
            # if the tags are not in JSON format, assume it's a comma-separated list and create an array
            tags_list = [t.strip() for t in tags_text.split(',')]
            return tags_list


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
    seen = models.BooleanField(
        null=False, blank=True, default=False,
        verbose_name=_("seen"),
        help_text=_("The notified user has seen the notification")
    )
    date_seen = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("date seen"),
        help_text=_("When the notification was seen")
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

    # tracking
    read_id = models.UUIDField(
        null=True, blank=True,
        verbose_name=_("read id"),
        help_text=_("ID to use for tracking the notification")
    )

    # extras
    date_created = models.DateTimeField(
        auto_now_add=True
    )
    last_changed = models.DateTimeField(
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

