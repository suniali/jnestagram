from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.views.generic import ListView,CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q,Count
from django.http import JsonResponse
from django.urls import reverse_lazy

from .models import Post, Tag,Like
from .form import PostForm

class PostListView(ListView):
    model = Post
    template_name = 'posts/home.html'
    context_object_name = 'posts'
    paginate_by = 10
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Post.objects.filter(is_active=True, is_public=True)
        queryset = queryset.annotate(
            approved_comments_count=Count(
                'comments', 
                filter=Q(comments__is_approved=True), 
                distinct=True
            ))
        tag_name = self.request.GET.get('tag')
        if tag_name:
            queryset = queryset.filter(tag__name=tag_name)
            
        return queryset.order_by('-created_at').distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['tags'] = Tag.objects.all()
        
        context['current_tag'] = self.request.GET.get('tag')
        
        top_posts= Post.objects.filter(is_active=True, is_public=True)
        top_posts=top_posts.annotate(
            score=Count('likes',distinct=True) +
            Count('comments', filter=Q(comments__is_approved=True),distinct=True)
        )
        context['top_posts']= top_posts.order_by('-score')[:4]

        return context

class PostCreateView(LoginRequiredMixin,CreateView):
    model=Post
    form_class=PostForm
    template_name="posts/post.html"
    success_url=reverse_lazy('home')
    
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['tags']=Tag.objects.all()
        return context
    
    def form_valid(self, form):
        form.instance.user=self.request.user
        tag_ids_str=self.request.POST.get('selected_tags','')
        response=super().form_valid(form)
        
        if tag_ids_str:
            try:
                tags=[int(tid) for tid in tag_ids_str.split(',') if tid.strip().isdigit()]
                self.object.tag.set(tags)
            except ValueError:
                pass
        return response
        

@require_POST
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    like,created=Like.objects.get_or_create(user=request.user, post=post)
    print(like)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'total_likes': post.total_likes()})
