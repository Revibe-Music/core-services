from django.db import models
from django.utils.translation import gettext_lazy as _

from revibe.utils.classes import default_repr
from revibe.utils.language.text import truncate_string

from .managers import ChatManager

# -----------------------------------------------------------------------------


class Chat(models.Model):
    first = models.ForeignKey(
        to='accounts.customuser',
        on_delete=models.CASCADE,
        related_name='chat_first',
        null=False, blank=False,
        verbose_name=_("first user"),
        help_text=_("The first user in the chat")
    )
    second = models.ForeignKey(
        to='accounts.customuser',
        on_delete=models.CASCADE,
        related_name='chat_second',
        null=False, blank=False,
        verbose_name=_("second user"),
        help_text=_("The second user in the chat")
    )

    created = models.DateTimeField(
        auto_now_add=True
    )
    updated = models.DateTimeField(
        auto_now=True
    )

    @property
    def group_name(self):
        return f"chat_{str(self.id)}"

    objects = ChatManager()

    def __str__(self):
        return f"{self.first.username} - {self.second.username}"

    def __repr__(self):
        return default_repr(self)

    class Meta:
        verbose_name = "chat"
        verbose_name_plural = "chats"


class Message(models.Model):
    chat = models.ForeignKey(
        to=Chat,
        on_delete=models.SET_NULL,
        related_name="chat",
        null=True, blank=False,
        verbose_name=_("chat"),
        help_text=_("The message that was sent")
    )
    user = models.ForeignKey(
        to='accounts.customuser',
        on_delete=models.CASCADE,
        related_name=_("chat_messages"),
        null=False, blank=False,
        verbose_name=_("sender"),
        help_text=_("The user that sent the message")
    )
    message = models.TextField(
        null=False, blank=False,
        verbose_name=_("message"),
        help_text=_("Message content")
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return truncate_string(self.message)

    def __repr__(self):
        return default_repr(self)

    class Meta:
        verbose_name = "message"
        verbose_name_plural = "messages"

