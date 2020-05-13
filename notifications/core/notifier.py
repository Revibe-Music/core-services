"""
Created: 07 May 2020
Author: Jordan Prechac
"""

from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags

import datetime
import random
import smtplib

import logging
logger = logging.getLogger(__name__)

from revibe._helpers import const
from revibe.contrib.queries.querysets import random_object

from administration.utils import retrieve_variable
from notifications.models import Event, Notification

from .config import base_email_config

# -----------------------------------------------------------------------------

class Notifier:
    def __init__(self, user, trigger, artist=False, force=False, medium='email', *args, **kwargs):
        self.user = user

        self.email = getattr(user.profile, 'email')
        if artist:
            self.artist = getattr(user, 'artist')
            artist_email = getattr(self.artist.artist_profile, 'email', None)
            if artist_email != None:
                self.email = artist_email
        else:
            self.artist = False

        self.mediums = self._validate_medium(medium)
        self.force = force

        self.event = self._get_event(trigger)
        self.templates = self.event.templates.filter(active=True)


    def _get_event(self, trigger):
        try:
            event = Event.objects.get(trigger=trigger)
        except Event.DoesNotExist:
            raise ValueError(f"Trigger '{trigger}' does not correspond to an Event")

        return event

    def _validate_medium(self, medium, *args, **kwargs):
        allowed_mediums = ['email','in_app','sms', 'push']
        if isinstance(medium, str):
            if medium not in allowed_mediums:
                raise ValueError(f"Medium '{medium}' is not a valid value")
            return [medium]

        elif isinstance(medium, list):
            errors = []
            mediums = []
            for med in medium:
                if medium not in allowed_mediums:
                    errors.append(f"Medium '{medium}' is not a valid value")
                else:
                    mediums.append(med)
            
            if errors:
                raise ValueError(str(errors))
            return mediums

        else:
            raise TypeError(f"Incorrect type for kwarg 'medium': {type(medium)}")

    def _configure_kwargs(self):
        """ Configure base kwargs for message formatting """
        config = base_email_config
        config['user'] = self.user
        config['artist'] = getattr(self, 'artist', None)

        return config

    def send_email(self):
        # don't send anything if the user doesn't let us
        if not self.user.profile.allow_email_notifications:
            return

        config = self._configure_kwargs()
        config['user'] = self.user
        config['username'] = self.user.username

        notification_template = random_object(self.templates.filter(medium='email'))

        from_address = getattr(self.event, 'from_address', '"Revibe" <noreply@revibe.tech>')

        # get message subject
        subject = getattr(notification_template, 'subject')
        if subject == None:
            subject = retrieve_variable('notification_email_subject_default', 'Revibe Notifications')

        # configure email body content
        html_format = notification_template.body
        html_message = html_format.format(**config)
        plain_message = strip_tags(html_message)

        try:
            sent = send_mail(
                subject=subject,
                message=plain_message,
                from_email=from_address,
                recipient_list=[self.email],
                html_message=html_message
            )
        except smtplib.SMTPException as e:
            self.mail_exception = e
            return False
        except Exception as e:
            self.mail_exception = e
            return False
        else:
            if (not sent) and settings.DEBUG:
                send_mail(
                    subject="Failed message",
                    message=f"Failed to send email message. Sent: '{sent}'",
                    from_email=from_address,
                    recipient_list=["jordanprechac@revibe.tech",]
                )
            elif sent:
                Notification.objects.create(
                    user=self.user,
                    event_template=notification_template,
                    is_artist=bool(getattr(self, 'artist', False))
                )

        return True

    def send_sms(self):
        # don't send anything if the user doesn't let us
        if not self.user.profile.allow_sms_notifications:
            return
        
        return

    def send_in_app(self):
        # don't send anything if the user doesn't let us
        if not self.user.profile.allow_in_app_notifications:
            return
        
        return

    def send_push(self):
        # don't send anything if the user doesn't let us
        if not self.user.profile.allow_push_notifications:
            return
        
        return

    def send(self, *args, **kwargs):
        """ Small function name for the send_notification method """
        return self.send_notification(*args, **kwargs)

    def send_notification(self, *args, **kwargs):
        # check that we can even send the user something
        if not self.force:
            # 4 day cooldown on sending stuff to artists
            # 7 day cooldown on sending stuff to users
            if self.artist:
                days = 4
            else:
                days = 7
            cooldown = datetime.timedelta(days=days)
            date_filter = datetime.datetime.now() - cooldown

            # get the notifications of this user in the last cooldown time
            # if the user has been sent a notification in that time, don't send them anything
            notifications = Notification.objects.filter(user=self.user, date_created__gte=date_filter)
            if notifications.count() >= 0:
                return False


        successes, fails = 0, 0
        for medium in self.mediums:
            func = getattr(self, f"send_{medium}")
            sent = bool(func())

            # log an error if the email couldn't be sent
            if not sent:
                logger.error(f"Failed to send notification. User: {str(self.user)}, Medium: {medium}.")
                fails += 1
            else:
                successes += 1

        return {"successes": successes, "fails": fails}



