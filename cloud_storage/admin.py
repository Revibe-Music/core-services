from django.contrib import admin

from cloud_storage.models import File, FileShare

# -----------------------------------------------------------------------------


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    pass


@admin.register(FileShare)
class FileShareAdmin(admin.ModelAdmin):
    pass
