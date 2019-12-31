from django.db import models

from uuid import uuid1


# Create your models here.

class ContactForm(models.Model):

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=False, blank=False)

    resolved = models.BooleanField(null=False, blank=False, default=False)
    assigned_to = models.CharField(max_length=255, null=True, blank=True)

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
    uri = models.CharField(max_length=255, null=False, blank=False, editable=False, unique=True, default=uuid1)
    name = models.CharField(max_length=255, null=False, blank=False)
    budget = models.IntegerField(null=False, blank=False)
    spent = models.IntegerField(null=True, blank=True)

