from django.contrib import admin

from .models import Post, Tag,Comment,Like

class CommentInline(admin.TabularInline):
    model = Comment
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
    inlines = [CommentInline]
    
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ( 'created_at',)
    search_fields = ('user__username', 'post__title')