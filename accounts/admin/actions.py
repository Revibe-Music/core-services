"""
"""

from revibe.utils import mailchimp

from accounts.utils.auth import reset_password

# -----------------------------------------------------------------------------


def update_mailchimp_info(modeladmin, request, queryset):
    for i in queryset:
        try:
            mailchimp.update_list_member(i)
        except Exception:
            pass
update_mailchimp_info.short_description = "Update Mailchimp list"

def admin_reset_password(modeladmin, request, queryset):
    for i in queryset:
        try:
            reset_password(user=i)
        except Exception:
            pass
admin_reset_password.short_description = "Reset password"

