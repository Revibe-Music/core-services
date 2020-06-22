"""
Created: 07 May 2020
Author: Jordan Prechac
"""

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.utils.html import strip_tags

import datetime
import random
import re
import smtplib
import sys

import logging
logger = logging.getLogger(__name__)

from revibe._helpers import const
from revibe.sharing.branch.models import song_link_from_template, album_link_from_template, artist_link_from_template
from revibe.template import render_html

from administration.utils import retrieve_variable
from content.models import Album, Song
from notifications.exceptions import NotificationException
from notifications.models import Event, Notification, NotificationTemplate
from notifications.utils.models.event import get_event, get_events
from notifications.utils.models.notification import create_notification_uuid

from .config import base_email_config

# -----------------------------------------------------------------------------

class Notifier:
    def __init__(self, user, trigger, artist=False, force=False, medium='email', check_first=False, extra_configs=None, *args, **kwargs):
        """
        """
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

        self._setup_album(kwargs.pop('album_id', None))
        self._setup_song(kwargs.pop('song_id', None))
        self._setup_contribution(kwargs.pop('contribution', None))

        self.event = self._get_event(trigger, check_first=check_first)
        self.templates = self.event.templates.filter(active=True)
        self.email_template = self.templates.filter(medium='email').order_by('?').first()

        self.extra_configs = extra_configs
        self.args = args
        self.kwargs = kwargs


    def _get_event(self, trigger, check_first=False):
        # if we are checking if its the first notification of this event:
        events = Event.active_objects.all()
        if check_first:
            # get the notifications this user has received about this event
            event_filter = Q(trigger=trigger) | Q(trigger=trigger+"-first")
            events = get_events(events, *(event_filter,))

            notifications = Notification.objects.filter(user=self.user, event_template__event__in=events)
            num_notifications = notifications.count()

            if num_notifications == 0:
                trigger += "-first"
            else:
                check_first=False

        try:
            return get_event(events, raise_exception=True, trigger=trigger)
        except Event.DoesNotExist:
            # if we're already not checking the first one
            if not check_first:
                logger.fatal("Failed to find notification event")
                raise NotificationException("Failed to find notification event")
                

            trigger = re.sub('\-first$', '', trigger)
            return self._get_event(trigger, check_first=False)

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

    def _setup_album(self, album_id):
        self.album = None
        if album_id:
            try:
                self.album = Album.hidden_objects.get(id=album_id)
            except Album.DoesNotExist:
                pass
        return self.album
    
    def _setup_song(self, song_id):
        self.song = None
        if song_id:
            try:
                self.song = Song.hidden_objects.get(id=song_id)
            except Song.DoesNotExist:
                pass
        return self.song
    
    def _setup_contribution(self, contribution):
        self.is_contribution = bool(contribution)
        if self.is_contribution:
            self.contribution = contribution

            try:
                if 'album_id' in self.contribution.keys():
                    self._setup_album(self.contribution.get("album_id"))
                elif 'song_id' in self.contribution.keys():
                    self._setup_song(self.contribution.get("album_id"))
            except Exception:
                pass

    def _configure_kwargs(self, template, **extras):
        """ Configure base kwargs for message formatting """
        config = base_email_config

        # add extra configs
        if isinstance(self.extra_configs, dict):
            config.update(self.extra_configs)

        config.update(extras)

        config['user'] = self.user
        config['username'] = self.user.username
        config['artist'] = getattr(self, 'artist', None)

        if config['artist'] not in  [None, False]:
            config['artist_name'] = self.user.artist.name
            config['artist_bio'] = self.user.artist.artist_profile.about_me
            config['artist_city'] = self.user.artist.artist_profile.city
            config['artist_state'] = self.user.artist.artist_profile.state
            config['artist_country'] = self.user.artist.artist_profile.country
            config['artist_zip_code'] = self.user.artist.artist_profile.zip_code
            try:
                image = self.artist.artist_image.filter(is_original.first())
                config['artist_image'] = image.url
            except Exception:
                config['artist_image'] = "Error getting Artist artwork"
            try:
                config['artist_deep_link'] = artist_link_from_template(self.user.artist, template)
            except Exception:
                config['artist_deep_link'] = retrieve_variable('home_website', 'https://revibe.tech')

        if self.album:
            config['album_name'] = self.album.name
            config['album_songs_count'] = self.album.songs.count()
            config['album_type'] = self.album.type
            config['album_uploader'] = self.album.uploaded_by.name
            try:
                image = self.album.album_image.filter(is_original=True).first()
                config['album_image'] = image.url
            except Exception:
                config['album_image'] = "Error getting Album artwork"
            try:
                config['album_deep_link'] = album_link_from_template(self.album, template)
            except Exception:
                config['album_deep_link'] = retrieve_variable('home_website', 'https://revibe.tech')

        if self.song:
            config['song_name'] = self.song.title
            config['song_uploader'] = self.song.song_uploaded_by.name
            # TODO: add song uploader name
            try:
                config['song_deep_link'] = song_link_from_template(self.song, template)
            except Exception:
                config['song_deep_link'] = retrieve_variable('home_website', 'https://revibe.tech')

        # temp
        if self.is_contribution:
            config['contribution_status'] = "approve" if self.contribution.get('approved', False) else "deny"
            config['contribution_status_past'] = "approved" if self.contribution.get('approved', False) else "denied"
            config['uploader_artist_name'] = self.contribution.get('artist_name', '-artist-')
            config['contribution_type'] = self.contribution.get('contribution_type','-contribution-')

        return config

    def configure_tracking_kwargs(self, tracking_id):
        kwargs = {}

        kwargs['tracking_id'] = tracking_id
        kwargs['tracking_link'] = f"https://api.revibe.tech/api/v1/notifications/images/{tracking_id}/"
        kwargs['tracking_html'] = """<div>
        <img src='{link}' width='1' height='1' />
        </div>""".format(link=kwargs['tracking_link'])

        return kwargs

    def format_html(self, html, config, template=None):
        if (template is None) or (template.render_version == NotificationTemplate.RENDER_V1):
            pieces = html.split('<body>')
            if len(pieces) <= 1:
                return pieces[0].format(**config)

            else:
                head, body = pieces

                body = body.format(**config)

                final = head + "<body>" + body

                return final
        else:
            # newer version of template rendering
            return render_html(html, config)


    def send_email(self):
        # don't send anything if the user doesn't let us
        if (not self.user.profile.allow_email_notifications) or (self.email_template is None):
            return

        # add the attribution/read-validation information
        notification_read_id = create_notification_uuid()
        notification_tracking_kwargs = self.configure_tracking_kwargs(notification_read_id)

        # add configuration stuff
        config = self._configure_kwargs(template=self.email_template, **notification_tracking_kwargs)

        from_address = getattr(self.event, 'from_address', '"Revibe" <noreply@revibe.tech>')

        # get message subject
        subject = getattr(self.email_template, 'subject')
        if subject == None:
            subject = retrieve_variable('notification_email_subject_default', 'Revibe Notifications')

        # configure email body content
        html_format = self.email_template.body
        html_message = self.format_html(html_format, config, self.email_template)
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
            raise e
            return False
        except Exception as e:
            self.mail_exception = e
            raise e
            return False
        else:
            if (not sent) and settings.DEBUG:
                send_mail(
                    subject="Failed message",
                    message=f"Failed to send email message. Sent to '{self.email}'",
                    from_email=from_address,
                    recipient_list=["jordanprechac@revibe.tech",]
                )
            elif sent:
                Notification.objects.create(
                    user=self.user,
                    event_template=self.email_template,
                    is_artist=bool(getattr(self, 'artist', False)),
                    read_id=notification_read_id
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
            print("User's notifications: ", notifications)
            if notifications.count() > 0:
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



