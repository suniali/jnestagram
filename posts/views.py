from django.views.generic import ListView
from django.db import models
from django.db.models import Q,Count

from .models import Post, Tag,Comment

class PostListView(ListView):
    model = Post
    template_name = 'posts/home.html'
    context_object_name = 'posts'
    paginate_by = 10
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        tag_name = self.request.GET.get('tag')
        if tag_name:
            queryset = queryset.filter(tag__name=tag_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        context['current_tag'] = self.request.GET.get('tag')
        context['top_posts']= Post.objects.annotate(
            score=Count('likes',distinct=True) + Count('comments', filter=Q(comments__is_approved=True),distinct=True)
        ).filter(is_active=True, is_public=True).order_by('-score')[:4]
        if context['current_tag'] is None:
            context['posts'] =Post.objects.annotate(
                approved_comments_count=Count('comments', filter=Q(comments__is_approved=True),distinct=True)).filter(
                    is_active=True, is_public=True).order_by('-created_at')
        else:
            context['posts'] = Post.objects.annotate(
                approved_comments_count=Count('comments', filter=Q(comments__is_approved=True),distinct=True)).filter(
                    is_active=True, is_public=True, tag__name=context['current_tag']).order_by('-created_at')
        return context