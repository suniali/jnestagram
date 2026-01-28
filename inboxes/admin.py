from django.contrib import admin

from .models import Conversation,Message

class MessageAdmin(admin.ModelAdmin):
    readonly_fields=('sender','text','conversation')

admin.site.register(Conversation)
admin.site.register(Message,MessageAdmin)