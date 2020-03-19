"""
"""

from revibe.utils import mailchimp

# -----------------------------------------------------------------------------


def update_mailchimp_info(modeladmin, request, queryset):
    for i in queryset:
        try:
            mailchimp.update_list_member(i)
        except Exception:
            pass
update_mailchimp_info.short_description = "Update Mailchimp list"
