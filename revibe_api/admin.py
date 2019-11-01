from django.contrib import admin
from revibe_api.models import CustomUser, Profile, Artist

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(Artist)