from revibe._helpers.files import add_track_to_song, add_image_to_obj
from revibe.utils import mailchimp

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
        add_track_to_song(obj, None, admin_edit=True)
reprocess_song.short_description = 'Reprocess selected song(s)'

def reprocess_image(modeladmin, request, queryset):
    for obj in queryset:
        related_name = f"{obj.__class__.__name__.lower()}_image"
        images = getattr(obj, related_name).filter(is_original=True)
        if len(images) == 0:
            continue

        original_image = images[0]
        add_image_to_obj(obj, original_image.file, edit=True, reprocess=True)
reprocess_image.short_description = "Reprocess selected objects' images"


def update_mailchimp_info(modeladmin, request, queryset):
    for i in queryset:
        try:
            mailchimp.update_list_member(i.artist_user, artist=True)
        except Exception:
            pass
update_mailchimp_info.short_description = "Update Mailchimp list"
