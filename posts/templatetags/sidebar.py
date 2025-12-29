from django.template import Library

from posts.models import Tag

register = Library()

@register.inclusion_tag('partials/sidebar.html')
def sidebar_view():
    tags=Tag.objects.all()
    context={'tags':tags}
    return context