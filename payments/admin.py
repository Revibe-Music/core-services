from django.contrib import admin

from revibe.utils.currency import format_currency

from .models import ThirdPartyDonation

# -----------------------------------------------------------------------------


@admin.register(ThirdPartyDonation)
class ThirdPartyDonationAdmin(admin.ModelAdmin):
    # customize list display
    list_display = (
        '__str__',
        '_display_recipient',
        '_display_donor',
        '_display_amount',
    )


    def _display_amount(self, obj):
        return format_currency(obj.amount)
    _display_amount.short_description = 'amount'
    _display_amount.admin_order_field = 'amount'

    def _display_recipient(self, obj):
        return str(obj.recipient) if obj.recipient else None
    _display_recipient.short_description = 'recipient'
    _display_recipient.admin_order_field = 'recipient__name'

    def _display_donor(self, obj):
        return (obj.donor.full_name if obj.donor.full_name else str(obj.donor.username)) if obj.donor else None
    _display_donor.short_description = 'donor'
    _display_donor.admin_order_field = 'donor__username'


