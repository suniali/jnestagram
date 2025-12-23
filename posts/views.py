from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404,redirect
from django.views.generic import ListView, CreateView, UpdateView, View, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q,Count,Prefetch
from django.http import JsonResponse
from django.urls import reverse_lazy,reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Post,Tag,Like,Comment
from .form import PostForm, CommentForm


class PostListView(ListView):
    model = Post
    template_name = 'posts/home.html'
    context_object_name = 'posts'
    paginate_by = 10
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Post.objects.filter(is_active=True, is_public=True).select_related(
            'user'
        ).prefetch_related(
            'tag'
        )

        queryset = queryset.annotate(
            approved_comments_count=Count(
                'comments', 
                filter=Q(comments__is_approved=True), 
                distinct=True
            )
        )
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
                messages.error(self.request, "Invalid tag id")
        messages.success(self.request, "Post successfully created")
        return response

    def get_success_url(self):
        next_url=self.request.GET.get('next')

        is_safe=url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts=self.request.get_host(),
            require_https=self.request.is_secure(),
        )
        if next_url and is_safe:
            return next_url
        return reverse_lazy('home')
        
class PostUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model=Post
    form_class=PostForm
    template_name='posts/post.html'
    success_url=reverse_lazy('home')
    
    def test_func(self):
        post=self.get_object()
        return self.request.user==post.user
    
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['tags']=Tag.objects.all()
        context['selected_tag_ids']=list(self.object.tag.values_list('id',flat=True))
        return context

    def form_valid(self, form):
        tags_id_str=self.request.POST.get('selected_tags','')
        response=super().form_valid(form)
        if tags_id_str:
            tags=[int(tid) for tid in tags_id_str.split(',') if tid.strip().isdigit()]
            self.object.tag.set(tags)
        else:
            self.object.tag.clear()
        messages.success(self.request, 'You have successfully updated your post.')
        return response

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        is_safe = url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        )

        if next_url and is_safe:
            return next_url
        return redirect('home')
    
class PostDeleteView(LoginRequiredMixin,UserPassesTestMixin,View):
    def test_func(self):
        post=get_object_or_404(Post, pk=self.kwargs['pk'])
        return post.user==self.request.user
    
    def post(self,request,*args,**kwargs):
        post=get_object_or_404(Post, pk=self.kwargs['pk'])

        post.is_active=False
        post.save()

        messages.success(request,'Your Post Deleted.')
        next_url=request.GET.get('next')
        is_secure=url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=self.request.is_secure(),
        )
        if next_url and is_secure:
            return redirect(next_url)
        return redirect('home')

    def get(self,request,*args,**kwargs):
        return  redirect('home')

class CommentCreateView(LoginRequiredMixin,CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "posts/comment.html"

    def get_queryset(self, **kwargs):
       return Comment.objects.select_related('user','post').filter(is_approved=True)

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        post=get_object_or_404(Post, pk=self.kwargs['pk'])
        approved_comments=self.get_queryset().filter(post=post).order_by('-created_at')

        context['post'] = post
        context['comments'] = approved_comments
        return context
    def form_valid(self, form):
        form.instance.user=self.request.user
        form.instance.post=Post.objects.get(pk=self.kwargs['pk'])

        if self.request.user.is_staff or  self.request.user.is_superuser:
            form.instance.is_approved=True
            messages.success(self.request,'Your comment has been published.')
        else:
            form.instance.is_approved=False
            messages.success(self.request, 'Your comment is awaiting approval.')

        return super().form_valid(form)
    def get_success_url(self):
        next_url=self.request.GET.get('next')
        is_secure=url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        )
        if next_url and is_secure:
            return next_url
        return reverse('add_comment',kwargs={'pk':self.kwargs['pk']})

class CommentUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "posts/comment_update.html"

    def test_func(self):
        comment=self.get_object()
        return self.request.user==comment.user

    def form_valid(self, form):
        form.instance.is_approved=False
        messages.info(self.request, "Your edit has been submitted and is awaiting re-approval.")
        return super().form_valid(form)

    def get_success_url(self):
        next_url=self.request.GET.get('next')
        is_secure=url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        )
        if next_url and is_secure:
            return next_url
        return reverse_lazy('add_comment',kwargs={'pk':self.object.post.pk})

class CommentDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Comment
    template_name = 'posts/comment_confirm_delete.html'

    def test_func(self):
        comment=self.get_object()
        return self.request.user==comment.user

    def get_success_url(self):
        messages.warning(self.request, "Comment deleted successfully.")
        next_url=self.request.GET.get('next')
        is_secure = url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        )
        if next_url and is_secure:
            return next_url
        return  reverse_lazy('add_comment',kwargs={'pk':self.object.post.pk})

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
