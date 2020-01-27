from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from uuid import uuid1

# -----------------------------------------------------------------------------

class ContactForm(models.Model):

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField("First Name", max_length=255, null=True, blank=True)
    last_name = models.CharField("Last Name", max_length=255, null=True, blank=True)
    email = models.CharField("Email", max_length=255, null=True, blank=True)
    subject = models.CharField("Contact form subject / type of request", max_length=255, null=True, blank=True) # going to be used as 'type'
    message = models.TextField("Message", null=False, blank=False)

    # administrative fields
    resolved = models.BooleanField("Indicates if the request/issue has been resolved or not", null=False, blank=False, default=False)
    assigned_to = models.CharField("Revibe staff member it's assigned to", max_length=255, null=True, blank=True)
    date_created = models.DateTimeField("When the form was submitted", auto_now_add=True, null=True)
    last_changed = models.DateTimeField("Last time the form was edited", auto_now=True, null=True)

    def __str__(self):
        if self.resolved:
            status = "RESOLVED"
        elif self.assigned_to == None:
            status = "UNASSIGNED"
        else:
            status = self.assigned_to
        string = "{status} - {id}".format(status=status, id=self.id)
        return string


class Campaign(models.Model):
    uri = models.CharField(max_length=255, null=False, blank=False, unique=True, default=uuid1)
    name = models.CharField(max_length=255, null=False, blank=False)
    budget = models.IntegerField(null=False, blank=False)
    spent = models.IntegerField(null=True, blank=True)


class YouTubeKey(models.Model):

    # id = models.AutoField(primary_key=True)
    key = models.CharField(
        help_text=_("API Key"),
        max_length=255,
        null=False, blank=False, unique=True
    )

    last_tested = models.DateTimeField(
        null=False, blank=True, default=timezone.now
    )
    worked_on_last_test = models.BooleanField(
        help_text=_("The last time this key was tested, it worked."),
        null=False, blank=True, default=True
    )

    date_created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        star = "" if self.worked_on_last_test else "*"
        return f"{star}{self.key}{star}"

    class Meta:
        verbose_name = 'YouTube Key'
        verbose_name_plural = 'YouTube Keys'

