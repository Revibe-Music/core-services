from django.db import models
from django.utils.translation import gettext_lazy as _

from revibe.utils.classes import default_repr

# -----------------------------------------------------------------------------


class Referral(models.Model):

    referrer = models.ForeignKey(
        to='accounts.CustomUser',
        on_delete=models.SET_NULL,
        related_name='referalls',
        null=True, blank=False,
        verbose_name=_("sent"),
        help_text=_("The user that did the referring")
    )

    referree = models.OneToOneField(
        to='accounts.CustomUser',
        on_delete=models.SET_NULL,
        related_name='referal',
        null=True, blank=False,
        verbose_name=_("referred"),
        help_text=_("The user that was referred")
    )

    referree_ip_address = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("referred IP address"),
        help_text=_("The IP address of the referree. Used for scam prevention")
    )

    # extras
    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.referrer} - {self.referree}"

    def __repr__(self):
        return default_repr(self)

    class Meta:
        verbose_name = "referral"
        verbose_name_plural = "referrals"



