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

    # images = many-to-one with content.Image
    # audio_files = many-to-one with content.Track

    price = models.DecimalField(
        max_digits=11, decimal_places=2,
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
    available = models.BooleanField(
        null=False, blank=True, default=True,
        verbose_name=_("available"),
        help_text=_("The item is currently available for sale")
    )
    repeating = models.BooleanField(
        null=False, blank=True, default=False,
        verbose_name=_("repeating"),
        help_text=_("The item is not limited to one purchase")
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


class Transaction(models.Model):

    good = models.ForeignKey(
        to='marketplace.good',
        on_delete=models.SET_NULL,
        related_name='transactions',
        null=True, blank=False,
        verbose_name=_("good"),
        help_text=_("Marketplace item")
    )

    buyer = models.ForeignKey(
        to='content.artist',
        on_delete=models.SET_NULL,
        related_name="transactions",
        limit_choices_to={"platform": "Revibe"},
        null=True, blank=False,
        verbose_name=_("buyer"),
        help_text=_("Artist who bought the good")
    )

    posted_price = models.DecimalField(
        max_digits=11, decimal_places=2,
        null=False, blank=False,
        verbose_name=_("posted price"),
        help_text=_("The listing price (including discounts) at the time of the transaction")
    )
    sale_price = models.DecimalField(
        max_digits=11, decimal_places=2,
        null=False, blank=False,
        verbose_name=_("sale price"),
        help_text=_("The amount actually paid")
    )

    returned = models.BooleanField(
        null=False, blank=True, default=False,
        verbose_name=_("returned"),
        help_text=_("The purchase was returned and refunded")
    )

    date_created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return str(self.good) if self.good else self.buyer if self.buyer else "literally no info on this one..."

    def __repr__(self):
        return classes.default_repr(self)
    
    class Meta:
        verbose_name = "transaction"
        verbose_name_plural = "transactions"

