from django.contrib import admin

from .models import GroupMessage,ChatGroup

@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ['group_name']

@admin.register(GroupMessage)
class GroupMessagesAdmin(admin.ModelAdmin):
    list_display = ['group', 'author','created_at']