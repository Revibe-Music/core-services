from revibe._helpers.files import add_track_to_song

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

