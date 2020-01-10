from django.db import models

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

