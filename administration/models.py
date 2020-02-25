from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import datetime
from uuid import uuid1

from revibe._helpers import const

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
        limit_choices_to={'is_staff': True},
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
    # create a class variable that keeps the required seconds to recheck the api key
    _check_time = 24 * 60 * 60 # one day in seconds
    _failure_threshold = 10

    # id = models.AutoField(primary_key=True)
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

    last_tested = models.DateTimeField(
        help_text=_("Time the key was last tested against the YouTube servers"),
        null=False, blank=True, default=timezone.now
    )
    worked_on_last_test = models.BooleanField(
        help_text=_("The last time this key was tested, it worked."),
        null=False, blank=True, default=True
    )
    failure_count = models.IntegerField(
        help_text="The number of failures without passing",
        null=False, blank=True, default=0
    )

    date_created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return str(self.key)
    
    def test_key(self):
        """
        Test the key against Youtube's API to determine if it's valid.
        """
        pass

    @property
    def recently_tested(self):
        """
        Return True if the key has been tested in the last day
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        difference = now - self.last_tested

        if difference.seconds < self._check_time:
            return True
        else:
            return False

    @property
    def is_valid(self):
        """
        Will return false if the key has failed more than the failure threshold.
        """
        return True
        # if self.failure_count >= self._failure_threshold:
        #     return False
        # else:
        #     return True

    class Meta:
        verbose_name = 'YouTube Key'
        verbose_name_plural = 'YouTube Keys'
        ordering = ['-point_budget']

