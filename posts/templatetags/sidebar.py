from django.template import Library
from django.db.models import Prefetch

from posts.models import Tag,Post,Like

register = Library()

@register.inclusion_tag('partials/sidebar.html')
def sidebar_view(current_tag=None,user=None):
    tags=Tag.objects.all()
    top_posts=Post.objects.select_related('user').prefetch_related(
        Prefetch('likes',queryset=Like.objects.select_related('user'),to_attr='likess')
    ).filter(
        is_active=True,
        is_public=True,
        likes_count__gt=0
    ).order_by('-likes_count','-comments_count')[:4]
    context={'tags':tags,'top_posts':top_posts,'current_tag':current_tag,'user':user}
    return context

@register.filter
def is_liked_by(obj,user):
    if user.is_anonymous:
        return False

    return any(like.user_id == user.id for like in obj.likess)