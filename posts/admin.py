from django.contrib import admin

from .models import Post, Tag,Comment,Like,Replay

class ReplayInline(admin.TabularInline):
    model = Replay
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('slug',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_active', 'is_public', 'created_at', 'updated_at')
    list_filter = ('is_active', 'is_public', 'created_at')
    search_fields = ('title', 'text', 'user__username')
    filter_horizontal = ('tag',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user','post', 'text','is_approved', 'created_at')
    list_filter = ('is_approved','created_at')
    search_fields = ('text','post',)
    inlines = [ReplayInline]
