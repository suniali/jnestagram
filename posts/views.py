
from django.shortcuts import get_object_or_404,redirect,render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView,DetailView,View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Prefetch,OuterRef,Exists,Value,BooleanField,CharField
from django.db.models.functions import Cast
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse,reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Post,Tag,Like,Comment,Replay
from .form import PostForm, CommentForm,ReplayForm


class PostListView(ListView):
    model = Post
    template_name = 'posts/home.html'
    context_object_name = 'posts'
    paginate_by =10

    def get_queryset(self):
        queryset = Post.objects.filter(is_active=True, is_public=True).select_related(
            'user'
        ).prefetch_related(
            'tag',
        )

        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tag__slug=tag_slug)


        if self.request.user.is_authenticated:
            post_type = ContentType.objects.get_for_model(Post)
            user_likes=Like.objects.filter(
                user=self.request.user,
                content_type=post_type,
                object_id=Cast(OuterRef('pk'),CharField()),
            )
            queryset = queryset.annotate(is_liked=Exists(user_likes))
        else:
            queryset = queryset.annotate(is_liked=Value(False,output_field=BooleanField()))

        return queryset.order_by('-created_at').distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['current_tag'] = self.request.GET.get('tag')

        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        replays=Replay.objects.select_related('user','comment').prefetch_related('likes')
        approved_comments=Comment.objects.filter(is_approved=True).select_related('user','post').prefetch_related('likes')
        queryset= Post.objects.filter(is_active=True).select_related('user').prefetch_related('tag','likes')

        if self.request.user.is_authenticated:
            post_type = ContentType.objects.get_for_model(Post)
            comment_type = ContentType.objects.get_for_model(Comment)
            replay_type=ContentType.objects.get_for_model(Replay)
            user_post_likes=Like.objects.filter(
                user=self.request.user,
                content_type=post_type,
                object_id=Cast(OuterRef('pk'),CharField()),
            )
            user_comment_likes=Like.objects.filter(
                user=self.request.user,
                content_type=comment_type,
                object_id=Cast(OuterRef('pk'),CharField()),
            )
            user_replay_likes=Like.objects.filter(
                user=self.request.user,
                content_type=replay_type,
                object_id=Cast(OuterRef('pk'),CharField()),
            )
            queryset = queryset.annotate(is_liked=Exists(user_post_likes))
            approved_comments=approved_comments.annotate(is_liked=Exists(user_comment_likes))
            replays=replays.annotate(is_liked=Exists(user_replay_likes))
        else:
            queryset = queryset.annotate(is_liked=Value(False,output_field=BooleanField()))
            approved_comments=approved_comments.annotate(is_liked=Value(False,output_field=BooleanField()))
            replays=replays.annotate(is_liked=Value(False,output_field=BooleanField()))

        approved_comments=approved_comments.prefetch_related(
            Prefetch('comment_replays', queryset=replays, to_attr='replies'),
        )

        top_comments=approved_comments.filter(likes_count__gt=0).order_by('-likes_count')[:4]
        queryset=queryset.prefetch_related(
            Prefetch('post_comments', queryset=approved_comments,to_attr='approved_comments_list'),
            Prefetch('post_comments', queryset=top_comments, to_attr='top_comments'),
        )

        return queryset

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        post=self.object

        if 'top' in self.request.GET:
            comments = post.top_comments
        else:
            comments=post.approved_comments_list

        context['display_comments']=comments
        context['current_tag'] = self.request.GET.get('tag')

        context['top_posts'] = Post.objects.select_related('user').prefetch_related(
            'tag',
            'likes'
        ).filter(
            is_active=True,
            is_public=True,
            likes_count__gt=0
        ).order_by('-likes_count','-comments_count')[:4]

        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.htmx:
            return render(
                self.request,
                'partials/posts/comments_container.html',
                {'display_comments': context['display_comments'],'post':self.object},)

        return super().render_to_response(context, **response_kwargs)

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
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.select_related('user').prefetch_related('tag','likes')
    
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


class CommentCreateView(LoginRequiredMixin,CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "posts/post_detail.html"

    def form_valid(self, form):
        form.instance.user=self.request.user
        form.instance.post_id=self.kwargs['pk']

        post=get_object_or_404(Post,pk=self.kwargs['pk'])

        if self.request.user.is_staff or  self.request.user.is_superuser or self.request.user == post.user:
            form.instance.is_approved=True
            msg='Your comment has been published.'
        else:
            form.instance.is_approved=False
            msg='Your comment is awaiting approval.'

        self.object=form.save()

        if self.request.htmx:
            comment=Comment.objects.select_related('user','post','post__user').get(pk=self.object.id)
            response=render(self.request,'partials/posts/add_comment.html',{
                                'comment':comment,
                                'post':comment.post,
                                'msg':msg,
                            })
            return response

        messages.success(self.request, msg)
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
        return self.request.user==comment.post.user

    def form_valid(self, form):
        form.instance.is_approved=False
        messages.info(self.request, "Your edit has been submitted and is awaiting re-approval.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post_detail',kwargs={'pk':self.object.post.pk})

class CommentDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Comment
    template_name = 'layouts/generic_delete.html'
    success_url = reverse_lazy('post_detail')

    def test_func(self):
        comment=self.get_object()
        return self.request.user==comment.post.user

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        post_id=self.object.post.id
        context['object_type']=f'Comment : {self.object.text}'
        context['cancel_url']=reverse_lazy('post_detail',kwargs={'pk':post_id})
        return context

    def get_success_url(self):
        messages.warning(self.request, "Comment deleted successfully.")

        post_id=self.object.post.id
        return reverse('post_detail',kwargs={'pk':post_id})

class ReplayCreateView(LoginRequiredMixin,View):
    def post(self,request,*args,**kwargs):
        form = ReplayForm(request.POST)

        comment = get_object_or_404(Comment, pk=kwargs['pk'])

        if form.is_valid():
            replay = form.save(commit=False)
            replay.user = request.user
            replay.comment = comment
            replay.save()
            messages.success(request, 'Your replay has been published.')
        else:
            messages.error(request, 'Error submitting your replay.')


        next_url = request.GET.get('next')
        is_secure = url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        )

        if next_url and is_secure:
            return redirect(next_url)

        count=Replay.objects.filter(comment=comment).count()


        return render(request,"partials/posts/add_replay.html",{'replay':replay,'comment':comment,'count':count})

class ReplayDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Replay
    template_name = 'layouts/generic_delete.html'
    def test_func(self):
        replay=self.get_object()
        user=replay.comment.post.user
        return self.request.user==user

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        replay=self.get_object()
        context['object_type'] = f'Replay : {replay.text}'
        context['cancel_url']=reverse_lazy('post_detail',kwargs={'pk':replay.comment.post.pk})
        return context
    def get_success_url(self):
        messages.warning(self.request, "Replay deleted successfully.")
        post_id=self.get_object().comment.post.pk

        next_url=self.request.GET.get('next')
        is_secure = url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        )

        if next_url and is_secure:
            return next_url

        return  reverse('post_detail',kwargs={'pk':post_id})

class LikeView(LoginRequiredMixin,View):
    model = Like
    template_name = 'posts/home.html'
    def get(self, request,model_name,obj_id):
        if not request.user.is_authenticated:
            return HttpResponse(status=401)

        models_map={
            'post':Post,
            'comment':Comment,
            'replay':Replay,
        }

        target_model=models_map.get(model_name.lower())
        if not target_model:
            return HttpResponse('Model Not Found!',status=404)

        obj=get_object_or_404(target_model, pk=obj_id)

        with transaction.atomic():
            content_type=ContentType.objects.get_for_model(obj)
            object_id_str = str(obj.id)
            like_qs = Like.objects.filter(user=request.user, content_type=content_type,object_id=object_id_str)

            if like_qs.exists():
                like_qs.delete()
                is_liked=False
            else:
                Like.objects.get_or_create(
                    user=request.user,
                    content_type=content_type,
                    object_id=object_id_str
                )
                is_liked=True

            total_likes = Like.objects.filter(
                content_type=content_type,
                object_id=object_id_str
            ).count()

            obj.likes_count=total_likes
            obj.save(update_fields=['likes_count'])

        obj.is_liked = is_liked
        template_name=f'partials/likes/{model_name.lower()}_like.html'
        return render(request,template_name,{
                'obj':obj,
        })

