
def test_api_key(modeladmin, request, queryset):
    for ytkey in queryset:
        ytkey.test_key()
test_api_key.short_description = 'Test Key'


def reset_user_count(modeladmin, request, queryset):
    for ytkey in queryset:
        ytkey.number_of_users = 0
        ytkey.save()
reset_user_count.short_description = "Reset User Count"
