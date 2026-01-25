from django.db import transaction
from django.db.models import  Prefetch,Value,BooleanField,OuterRef,Exists,CharField
from django.db.models.functions import Cast

from django.contrib.contenttypes.models import ContentType

from django.contrib import messages

from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model,login,logout,update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin

from django.views.generic import View,CreateView,DetailView,DeleteView,UpdateView
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse_lazy

from .models import Profile,Country
from posts.models import Post, Comment, Like, Replay
from .forms import RegistrationForm,ProfileForm

User = get_user_model()

class RegisterView(CreateView):
    template_name = 'profiles/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('complate_profile')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user=form.save()
        login(self.request, user)
        messages.success(self.request,f'Welcome {user.username}! Your Account has been created.')
        return redirect(self.success_url)

class ComplateProfileView(LoginRequiredMixin,UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/complate_profile.html'
    success_url = reverse_lazy('profile')
    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def get_context_data(self, **kwargs):
        context=super().get_context_data()
        context['countries']=Country.objects.filter(is_active=True)
        return context
    def form_valid(self, form):
        messages.success(self.request,'Your profile has been updated.')
        return super().form_valid(form)
    
class CustomLoginView(LoginView):
    template_name = 'profiles/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('home')

    def form_invalid(self, form):
        messages.error(self.request,'Invalid credentials')
        return super().form_invalid(form)

class ProfileView(LoginRequiredMixin,View):
    template_name = 'profiles/profile.html'

    def get(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        users_posts=Post.objects.filter(user=request.user,is_active=True).order_by('-created_at')
        pending_comments=Comment.objects.filter(post__user=request.user,is_approved=False).select_related('user','post')
        countries=Country.objects.filter(is_active=True).order_by('name')
        context={
            'profile': profile,
            'user_posts':users_posts,
            'pending_comments':pending_comments,
            'countries':countries,
        }
        return render(request, self.template_name,context)
    
    def post(self, request):
        user=request.user
        profile, created = Profile.objects.get_or_create(user=user)
        
        email=request.POST.get('email')
        phone_number=request.POST.get('phone_number')
        country_id=request.POST.get('country')
        avatar=request.FILES.get('avatar')
        bio=request.POST.get('bio')
        
        # Update user and profile
        try:
            with transaction.atomic():
                if email and email != user.email:
                    if User.objects.filter(email=email).exclude(id=user.id).exists():
                        messages.error(request, 'This email is already in use.')
                        return redirect('profile')
                    user.email = email
                    user.save()
                
                profile.phone_number=phone_number
                if not profile.country and country_id:
                    try:
                        selected_country = Country.objects.get(id=country_id)
                        profile.country = selected_country
                    except (Country.DoesNotExist, ValueError):
                        messages.error(self.request,'Country Not Found!')
                if avatar:
                    profile.avatar=avatar

                profile.bio=bio
                profile.save()
                
                messages.success(request, 'Your profile has been updated successfully!')
        
        except Exception as e:
            messages.error(request, 'An error occurred. Please try again.')
            
        return redirect('profile')

class PublicProfileView(DetailView):
    model = Profile
    template_name = 'profiles/public_profile.html'
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get_queryset(self):
        queryset=Profile.objects.select_related('user','country')
        posts_qs=Post.objects.filter(is_active=True).order_by('-created_at')
        top_posts_qs=Post.objects.filter(is_active=True,likes_count__gt=0).order_by('-likes_count')[:5]
        top_comments_qs=Comment.objects.filter(is_approved=True,likes_count__gt=0).order_by('-likes_count','-replays_count')[:5]
        replays_qs=Replay.objects.select_related('user')

        if self.request.user.is_authenticated:
            post_type=ContentType.objects.get_for_model(Post)
            comment_type=ContentType.objects.get_for_model(Comment)
            replay_type=ContentType.objects.get_for_model(Replay)
            user_post_likes=Like.objects.filter(
                user=self.request.user,
                content_type=post_type,
                object_id=Cast(OuterRef('pk'),CharField())
            )
            user_comment_likes=Like.objects.filter(
                user=self.request.user,
                content_type=comment_type,
                object_id=Cast(OuterRef('pk'),CharField())
            )
            user_replay_likes=Like.objects.filter(
                user=self.request.user,
                content_type=replay_type,
                object_id=Cast(OuterRef('pk'),CharField())
            )
            posts_qs=posts_qs.annotate(is_liked=Exists(user_post_likes))
            top_comments_qs=top_comments_qs.annotate(is_liked=Exists(user_comment_likes))
            replays_qs=replays_qs.annotate(is_liked=Exists(user_replay_likes))
        else:
            posts_qs=posts_qs.annotate(is_liked=Value(False,output_field=BooleanField()))
            top_comments_qs=top_comments_qs.annotate(is_liked=Value(False,output_field=BooleanField()))
            replays_qs=replays_qs.annotate(is_liked=Value(False,output_field=BooleanField()))

        top_comments_qs=top_comments_qs.prefetch_related(
                Prefetch('comment_replays', queryset=replays_qs, to_attr='replies'),
        )

        queryset= queryset.prefetch_related(
            Prefetch('user__user_posts',queryset=posts_qs,to_attr='all_posts'),
            Prefetch('user__user_posts',queryset=top_posts_qs,to_attr='top_posts'),
            Prefetch('user__user_comments',queryset=top_comments_qs,to_attr='top_comments'),
        )
        return queryset

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)

        obj=self.object
        if 'top-posts' in self.request.GET:
            context['posts']=obj.user.top_posts
        elif 'top-comments' in self.request.GET:
            context['top_comments']=obj.user.top_comments
        else:
            context['posts']=obj.user.all_posts

        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.htmx:
            if 'top-posts' in self.request.GET:
                return render(self.request, 'partials/posts/posts_container.html', {'posts':context['posts']})
            elif 'top-comments' in self.request.GET:
                return render(self.request, 'partials/posts/comments_container.html', {'display_comments':context['top_comments']})
            else:
                return render(self.request, 'partials/posts/posts_container.html', {'posts': context['posts']})

        return super().render_to_response(context, **response_kwargs)
class UserDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = User
    template_name = 'layouts/generic_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        user=self.get_object()
        return self.request.user == user

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['object_type']=f'User : {self.request.user.username}'
        context['cancel_url']=reverse_lazy('profile')
        return context

@login_required
def approve_comment(request,pk):
    comment=get_object_or_404(Comment,pk=pk,post__user=request.user)
    comment.is_approved=True
    comment.save()
    messages.success(request, 'Comment has been approved and is now public.')
    return redirect('profile')