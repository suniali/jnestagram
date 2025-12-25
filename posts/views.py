from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404,redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.contrib import messages
from django.db.models import Prefetch,OuterRef,Exists,Value,BooleanField
from django.http import JsonResponse,HttpResponseRedirect
from django.urls import reverse,reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Post,Tag,Like,Comment
from .form import PostForm, CommentForm


class PostListView(ListView):
    model = Post
    template_name = 'posts/home.html'
    context_object_name = 'posts'
    paginate_by =10

    def get_queryset(self):
        queryset = Post.objects.filter(is_active=True, is_public=True).select_related(
            'user'
        ).prefetch_related(
            'tag'
        )

        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tag__slug=tag_slug)

        if self.request.user.is_authenticated:
            user_likes=Like.objects.filter(
                user=self.request.user,
                post_id=OuterRef('pk')
            )
            queryset = queryset.annotate(is_liked=Exists(user_likes))
        else:
            queryset = queryset.annotate(is_liked=Value(False,output_field=BooleanField()))

        return queryset.order_by('-created_at').distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['tags'] = Tag.objects.all()
        
        context['current_tag'] = self.request.GET.get('tag')
        
        top_posts= Post.objects.filter(is_active=True, is_public=True).order_by('-likes_count','-comments_count')[:4]

        context['top_posts']= top_posts
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        approved_comments=Comment.objects.filter(is_approved=True)

        return Post.objects.filter(is_active=True).select_related('user').prefetch_related(
            'tag',
            'likes',
            Prefetch('comments', queryset=approved_comments,to_attr='approved_comments_list')
        )

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)

        context['tags'] = Tag.objects.all()
        context['current_tag'] = self.request.GET.get('tag')

        context['top_posts'] = Post.objects.filter(is_active=True, is_public=True).order_by('-likes_count','-comments_count')[:4]

        return context

class PostCreateView(LoginRequiredMixin,CreateView):
    model=Post
    form_class=PostForm
    template_name="posts/post_create_update.html"
    
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['tags']=Tag.objects.all()
        return context
    
    def form_valid(self, form):
        form.instance.user=self.request.user

        self.object=form.save()

        tag_ids_str=self.request.POST.get('selected_tags','')
        if tag_ids_str:
            try:
                tags=[int(tid) for tid in tag_ids_str.split(',') if tid.strip().isdigit()]
                self.object.tag.set(tags)
            except ValueError:
                messages.warning(self.request, "Post created, but some tags were invalid.")

        messages.success(self.request, "Post successfully created")

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        next_url=self.request.GET.get('next')

        is_safe=url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts=self.request.get_host(),
            require_https=self.request.is_secure(),
        )
        if next_url and is_safe:
            return next_url
        return reverse('post_detail', kwargs={'pk':self.object.pk})
        
class PostUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model=Post
    form_class=PostForm
    template_name='posts/post_create_update.html'

    def get_queryset(self):
        return Post.objects.prefetch_related('tag')
    
    def test_func(self):
        post=self.get_object()
        return self.request.user==post.user
    
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)

        context['tags']=Tag.objects.all()

        if self.object:
            context['selected_tag_ids']=list(self.object.tag.values_list('id',flat=True))
        else:
            context['selected_tag_ids']=[]

        return context

    def form_valid(self, form):
        self.object=form.save()

        tags_id_str=self.request.POST.get('selected_tags','')
        if tags_id_str:
            try:
                tags=[int(tid) for tid in tags_id_str.split(',') if tid.strip().isdigit()]
                self.object.tag.set(tags)
            except (ValueError,TypeError):
                messages.error(self.request, 'There was an error processing tags.')
        else:
            self.object.tag.clear()

        messages.success(self.request, 'You have successfully updated your post.')

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        is_safe = url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        )

        if next_url and is_safe:
            return next_url

        return reverse('post_detail', kwargs={'pk':self.object.pk})
    
class PostDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Post
    template_name = 'posts/post_delete.html'
    success_url = reverse_lazy('home')
    def test_func(self):
        post=self.get_object()
        return post.user==self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Post successfully deleted.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        next_url=self.request.GET.get('next')

        is_safe = url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts=self.request.get_host(),
            require_https=self.request.is_secure(),
        )

        if next_url and is_safe:
            return next_url

        return str(self.success_url)

class CommentCreateView(LoginRequiredMixin,CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "posts/comment.html"

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)

        post=get_object_or_404(Post, pk=self.kwargs['pk'])

        approved_comments= Comment.objects.select_related('user').filter(
            post=post,
            is_approved=True
        ).order_by('-created_at')

        context['post'] = post
        context['comments'] = approved_comments
        return context
    def form_valid(self, form):
        form.instance.user=self.request.user

        form.instance.post_id=self.kwargs['pk']

        if self.request.user.is_staff or  self.request.user.is_superuser:
            form.instance.is_approved=True
            messages.success(self.request,'Your comment has been published.')
        else:
            form.instance.is_approved=False
            messages.info(self.request, 'Your comment is awaiting approval.')

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

        return reverse('post_detail',kwargs={'pk':self.kwargs['pk']})

class CommentUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "posts/comment_update.html"

    def get_queryset(self):
        return super().get_queryset().select_related('user','post')

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

        return reverse('post_detail',kwargs={'pk':self.object.post.pk})

class CommentDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Comment
    template_name = 'posts/comment_confirm_delete.html'
    success_url = reverse_lazy('post_detail')

    def test_func(self):
        comment=self.get_object()
        return self.request.user==comment.user or self.request.user==comment.post.user

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

        return  str(self.success_url)

@require_POST
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post.objects.only('id'), pk=post_id)

    like_queryset=Like.objects.filter(user=request.user, post=post)

    if like_queryset.exists():
        like_queryset.delete()
        liked = False
    else:
        like_queryset.create(user=request.user, post=post)
        liked = True

    total_likes=post.likes_count

    return JsonResponse({'liked': liked, 'total_likes': total_likes})
