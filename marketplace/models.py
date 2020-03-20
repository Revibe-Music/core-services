from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from revibe.contrib.models import fields
from revibe.utils import classes

from marketplace import managers
from marketplace.utils.models.good import discounted_price

# -----------------------------------------------------------------------------


class Good(models.Model):

    _category_choices = (
        ('product', 'Product'),
        ('service', 'Service'),
    )
    category = models.CharField(
        max_length=100,
        choices=_category_choices,
        null=False, blank=False,
        verbose_name=_("category"),
        help_text=_("Either a 'product' or 'service' offering")
    )

    name = models.CharField(
        max_length=255,
        null=False, blank=False,
        verbose_name=_("name"),
        help_text=_("Display name for the product or service")
    )
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_("description"),
        help_text=_("Item description")
    )

    image = models.FileField(
        null=True, blank=True,
        verbose_name=_("image"),
        help_text=_("Image to display for this good")
    )
    audio = models.FileField(
        null=True, blank=True,
        verbose_name=_("audio"),
        help_text=_("Audio or audio sample for the good")
    )

    price = models.DecimalField(
        max_digits=6, decimal_places=2,
        null=False, blank=False,
        verbose_name=_("price"),
        help_text=_("The price of the product or service")
    )
    discount = fields.IntegerRangeField(
        min_value=0, max_value=100,
        null=False, blank=False, default=0,
        verbose_name=_("discount"),
        help_text=_("The percentage discount of the good")
    )

    publish_date = models.DateField(
        null=False, blank=True, default=timezone.now,
        verbose_name=_("publish date"),
        help_text=_("Date the good will go public")
    )

    seller = models.ForeignKey(
        to='content.artist',
        on_delete=models.SET_NULL,
        limit_choices_to={'platform': 'Revibe'},
        related_name="sale_goods",
        null=True, blank=False,
        verbose_name=_("seller"),
        help_text=_("Seller of the good. Must be a Revibe artist")
    )
    purchaser = models.ForeignKey(
        to='content.artist',
        on_delete=models.SET_NULL,
        limit_choices_to={'platform': 'Revibe'},
        related_name="purchased_goods",
        null=True, blank=True, default=None,
        verbose_name=_("purchaser"),
        help_text=_("Purchaser of the good. Must be a Revibe artist")
    )
    sold = models.BooleanField(
        null=False, blank=False, default=False,
        verbose_name=_("sold status"),
        help_text=_("Shows the item has been sold or not")
    )
    sale_date = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("sale date"),
        help_text=_("The date and time the good was sold")
    )

    date_created = models.DateTimeField(
        auto_now_add=True
    )
    last_changed = models.DateTimeField(
        auto_now=True
    )

    # objects = managers.GoodObjectsManager()

    @property
    def discounted_price(self):
        return discounted_price(self.price, self.discount)

    def __str__(self):
        return self.name

    def __repr__(self):
        return classes.default_repr(self)
    
    class Meta:
        verbose_name = "good"
        verbose_name_plural = "goods"

