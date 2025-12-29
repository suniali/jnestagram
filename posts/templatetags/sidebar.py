from django.template import Library

from posts.models import Tag,Post

register = Library()

@register.inclusion_tag('partials/sidebar.html')
def sidebar_view():
    tags=Tag.objects.all()
    top_posts=Post.objects.filter(is_active=True, is_public=True,likes_count__gt=0).order_by('-likes_count','-comments_count')[:4]
    context={'tags':tags,'top_posts':top_posts}
    return context