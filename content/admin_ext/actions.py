from revibe._helpers.files import add_track_to_song, add_image_to_obj

# -----------------------------------------------------------------------------

def perform_delete(modeladmin, request, queryset):
    queryset.update(is_deleted=True, is_displayed=False)
perform_delete.short_description = "Delete the selected objects"

def remove_delete(modeladmin, request, queryset):
    queryset.update(is_deleted=False, is_displayed=True)
remove_delete.short_description = "Un-delete the selected objects"


def approve_contribution(modeladmin, request, queryset):
    queryset.update(approved=True, pending=False)
approve_contribution.short_description = "Approve selected contributions"


def reprocess_song(modeladmin, request, queryset):
    for obj in queryset:
        tracks = obj.tracks.filter(is_original=True)
        if len(tracks) == 0:
            continue

        original_track = tracks[0]
        add_track_to_song(obj, original_track.file, edit=True)
reprocess_song.short_description = 'Reprocess selected songs'

def reprocess_image(modeladmin, request, queryset):
    for obj in queryset:
        related_name = f"{obj.__class__.__name__.lower()}_image"
        images = getattr(obj, related_name).filter(is_original=True)
        if len(images) == 0:
            continue

        original_image = images[0]
        add_image_to_obj(obj, original_image.file, edit=True)
reprocess_image.short_description = "Reprocess selected objects' images"

