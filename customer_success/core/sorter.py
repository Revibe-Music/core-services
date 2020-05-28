"""
Created: 28 May 2020
Author: Jordan Prechac
"""

from django.db.models import QuerySet

import random

from administration.utils import retrieve_variable
from customer_success.exceptions import CustomerSuccessException
from customer_success.models import Action, Pathway, PathwayAction, ActionTaken
from notifications.tasks import send_notification


# -----------------------------------------------------------------------------


class Sorter:
    rankings = [ p[0] for p in PathwayAction._priority_choices ]

    def __init__(self, user, is_artist=False, run_async=False, *args, **kwargs):
        self.user = user
        self.is_artist = is_artist
        self.run_async = run_async

        self._get_paths()

        self.action_minimum = retrieve_variable("customer-success_minimum-action-cutoff", 3, output_type=int)
        self.action_completion = retrieve_variable("customer-success_action-completion-rate", 0.6, output_type=float)
        if self.action_completion > 1:
            self.action_completion = 1
        elif self.action_completion < 0:
            self.action_completion = 0

    def _get_paths(self):
        # get the user's paths
        filtr = Pathway.ARTIST if self.is_artist else Pathway.LISTENER
        paths = self.user.cs_paths.filter(type=filtr)

        # if there are none, use the defaults
        if not paths:
            if self.is_artist:
                paths = Pathway.objects.filter(type=Pathway.ARTIST, default=True)
            else:
                paths = Pathway.objects.filter(type=Pathway.LISTENER, default=True)

        self.paths = paths
        return self.paths

    def get_actions(self):
        usable_actions = []
        for path in self.paths:
            for rank in self.rankings:
                # get the actions in the level of the path
                available_actions = Action.objects.filter(pathwayactions__ranking=rank, pathways=path, active=True)
                num_available_actions = available_actions.count()

                # skip to the next rank if there are no actions
                if not num_available_actions:
                    continue

                # get the actions the user has completed
                completed_actions = available_actions.filter(actions_taken__user=self.user)
                num_completed_actions = completed_actions.count()

                # add incomplete actions to the usable actions
                for a in available_actions.exclude(actions_taken__user=self.user):
                    usable_actions.append(a)

                # decide if we should move on to the next rank
                # move to next if either:
                #   - number of available actions is less than 3
                #   - the user has completed the quota of the available actions
                quota = getattr(path, f"{rank}_quota", self.action_completion)
                quota = quota if quota != None else self.action_completion
                to_continue = (num_available_actions < self.action_minimum) or ( (num_completed_actions / num_available_actions ) >= quota )
                if not to_continue:
                    break

        self.usable_actions = Action.objects.filter(active=True, id__in=[a.id for a in usable_actions])
        return self.usable_actions

    def pick_action(self, actions=None, require_event=True):
        """
        Picks a random action from the actions argument or the class 'usable_actions'.

        TODO: implement some algorithm to pick actions, not just randomizing stuff
        """
        # get the list of actions
        if actions == None:
            try:
                actions = getattr(self, 'usable_actions')
            except AttributeError:
                raise CustomerSuccessException("'pick_action' method could not find any valid actions")


        if isinstance(actions, QuerySet):
            if require_event:
                actions = actions.filter(event__isnull=False, event__active=True)
            action = actions.order_by('?').first()

        else:
            # pick a random action from the list of actions
            action = random.choice(actions)

        self.action = action
        return self.action

    def send_notification(self):
        action = self.pick_action(self.get_actions())

        # if there are no available actions, return
        if not action:
            return False

        args = (self.user.id, action.event.trigger, )
        kwargs = {
            "artist": self.is_artist,
        }

        if self.run_async:
            send_notification.delay(
                *args, **kwargs
            )
            return True
        else:
            return send_notification(
                *args, **kwargs
            )

