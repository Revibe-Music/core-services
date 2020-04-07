from django.contrib import admin

from .models import Chat, Message

# -----------------------------------------------------------------------------

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    pass


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass

