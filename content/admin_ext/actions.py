

def perform_delete(modeladmin, request, queryset):
    queryset.update(is_deleted=True, is_displayed=False)
perform_delete.short_description = "Delete the selected object(s)"

def remove_delete(modeladmin, request, queryset):
    queryset.update(is_deleted=False, is_displayed=True)
remove_delete.short_description = "Un-delete the selected object(s)"
