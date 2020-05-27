"""
Created: 21 May 2020
Author: Jordan Prechac
"""

from django.db.models import Q
from django.utils import timezone

from datetime import timedelta

from customer_success.models import Action, ActionTaken
from customer_success.exceptions import CustomerSuccessException
from notifications.models import Notification

# -----------------------------------------------------------------------------

class Attributor:
    def __init__(self, user, name, *args, **kwargs):

        self.user = user

        self.args = args
        self.kwargs = kwargs

        # get the Action this is related to
        self.action = self._get_action(name)


    def attribute(self):
        # steps
        # 1. get notifications user has received related to events that are
        #    associated with this action
        # 2. if there are events,
        #    mark the most recent nofication as having been successful, and mark the datetime
        # 3. Record that this user performed this action


        # 1.
        core_event = self.action.event
        extra_events = self.action.extra_events.all()
        if (core_event or extra_events.count()):
            # raise CustomerSuccessException("Action has no events")

            # get the action's event info
            core_event_id = getattr(core_event, 'id', None)
            extra_events_ids = [e[0] for e in extra_events.values_list('id')]

            # generate notification filters
            notification_event_filter = Q(event_template__event__id=core_event_id) | Q(event_template__event__id__in=extra_events_ids)
            notification_filter_args = (notification_event_filter,)
            notification_filter_kwargs = {
                "user": self.user,
                "date_created__gte": self._action_date_filter()
            }

            # query for notifications
            notifications = Notification.objects.filter(*notification_filter_args, **notification_filter_kwargs)
            notifications = notifications.distinct()

            # 2. 
            if notifications.count() > 0:
                # get the most recent notification
                notifications = notifications.order_by('-date_created')
                notif = notifications.first()

                # change it's info
                if not notif.action_taken:
                    notif.action_taken = True
                    notif.date_of_action = timezone.now()
                    notif.save()

                self.notif = notif
        else:
            self.notif = None

        # 3.
        ActionTaken.objects.create(action=self.action, user=self.user, notification=self.notif)

        return


    # helper functions
    def _get_action(self, name):
        try:
            action = Action.objects.filter(active=True).get(name=name)
        except Action.DoesNotExist as e:
            raise CustomerSuccessException(str(e))

        self.action = action
        return self.action

    def _action_date_filter(self):
        now = timezone.now()
        diff = timedelta(**{self.action.interval_period: self.action.number_of_period})

        return now - diff

