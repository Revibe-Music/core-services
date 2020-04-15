"""
Created: 30 Mar. 2020
Author: Jordan Prechac
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from revibe.utils.classes import default_repr
# -----------------------------------------------------------------------------


class ThirdPartyDonation(models.Model):

    recipient = models.ForeignKey(
        to='content.artist',
        on_delete=models.SET_NULL,
        related_name='third_party_donations_received',
        limit_choices_to={'platform': 'Revibe'},
        null=True, blank=False,
        verbose_name=_("recipient"),
        help_text=_("The artist who recieved the donation")
    )
    donor = models.ForeignKey(
        to='accounts.customuser',
        on_delete=models.SET_NULL,
        related_name='third_party_donations_made',
        null=True, blank=True,
        verbose_name=_("donor"),
        help_text=_("The user who made the donation")
    )

    service = models.CharField(
        max_length=255,
        null=False, blank=False,
        verbose_name=_("payment service"),
        help_text=_("Payment service that the user made the donation through")
    )
    amount = models.DecimalField(
        max_digits=11, decimal_places=2,
        null=True, blank=True,
        verbose_name=_("donation amount"),
        help_text=_("Amount donated to the artist")
    )
    other = models.BooleanField(
        null=True, blank=True,
        verbose_name=_("other"),
        help_text=_("Indicates that the user picked an 'other' payment amount")
    )

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return str(self.id)
        # return str(self.recipient) if self.recipient else '-no longer an artist-'

    def __repr__(self):
        return default_repr(self)

    class Meta:
        verbose_name = "third party donation"
        verbose_name_plural = "third party donations"

