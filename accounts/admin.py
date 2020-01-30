from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', 'date_joined', '_full_name')
    list_filter = (
        ('date_joined', admin.DateFieldListFilter),
        ('is_staff', admin.BooleanFieldListFilter),
    )
    # customize actions
    # actions = [change_password]

    def _full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


admin.site.register(Profile)


admin.site.register(Social)


admin.site.register(ArtistProfile)
