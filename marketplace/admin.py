from django.contrib import admin

from marketplace.models import *

# -----------------------------------------------------------------------------

@admin.register(Good)
class GoodAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('sortable_str', '_format_price', '_format_discounted_price')

    # customize list filter
    list_filter = (
        ('purchaser', admin.RelatedOnlyFieldListFilter),
        ('seller', admin.RelatedOnlyFieldListFilter),
        ('sold', admin.BooleanFieldListFilter),
        'category',
    )

    # customize search
    search_fields = [
        'name',
        'description',
        'seller__name',
        'seller__artist_user__username',
        'purchaser__name',
        'purchaser__artist_user__username',
    ]

    def sortable_str(self, obj):
        return obj.__str__()
    sortable_str.short_description = 'name'
    sortable_str.admin_order_field = 'name'

    def _format_price(self, obj):
        return '${:,.2f}'.format(obj.price)
    _format_price.short_description = 'price'
    _format_price.admin_order_field = 'price'

    def _format_discounted_price(self, obj):
        return '${:,.2f} ({}%)'.format(obj.discounted_price, obj.discount)
    _format_discounted_price.short_description = 'discounted price'
    _format_discounted_price.admin_order_field = 'discount'

