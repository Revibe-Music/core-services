
def test_api_key(modeladmin, request, queryset):
    for ytkey in queryset:
        ytkey.test_key()
test_api_key.short_description = 'Test Key'

