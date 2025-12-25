from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model,login,logout,authenticate,update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.shortcuts import render,redirect,get_object_or_404

from .models import Profile
from posts.models import Post,Comment

User = get_user_model()

class RegisterView(View):
    template_name = 'profiles/register.html'

    def get(self,request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request,self.template_name)

    def post(self,request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Basic validation
        if not all([username, email, password1, password2]):
            messages.error(request, 'All fields are required.')
            return render(request, self.template_name)

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, self.template_name)

        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, self.template_name)
        

        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            user.save()
            login(request, user)  # Auto-login after registration
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('home')
        except IntegrityError:
            messages.error(request, 'Username or email is already taken.')
        except ValidationError as e:
            messages.error(request, str(e))

        return render(request, self.template_name)
    
class LoginView(View):
    template_name = 'profiles/login.html'
    
    def get(self,request):
        if request.user.is_authenticated:
            return redirect('home')
        
        return render(request,self.template_name)
    
    def post(self,request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', request.GET.get('next', 'home'))
        
        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, self.template_name)

        user = authenticate(username=username, password=password)
        if user is None:
            messages.error(request, 'Invalid username or password.')
            return render(request, self.template_name)

        login(request, user)
        return redirect(next_url)
    
class LogoutView(View):
    def get(self,request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('login')
    
class ForgotPasswordView(View):
    template_name = 'profiles/forgot_password.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, self.template_name)

    def post(self, request):
        username=request.POST.get('username')
        print(username)

        if not username:
            messages.error(request, 'Please provide your username.')
            return render(request, self.template_name)
        
        user=User.objects.filter(username=username).first()
        if not user:
            messages.error(request, 'No account found with that username.')
            return render(request, self.template_name)
        
        return redirect('reset_password', username=user.username)
    
class ResetPasswordView(View):
    template_name = 'profiles/reset_password.html'

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Invalid or expired reset link.')
            return redirect('login')
            
        return render(request, self.template_name, {'username': username})
        
    def post(self, request, username):
        try:
            user=User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Invalid request.')
            return redirect('login')
            
        password1=request.POST.get('password1')
        password2=request.POST.get('password2')
            
        if not password1 or not password2:
            messages.error(request, 'Please fill out all fields.')
            return render(request, self.template_name, {'username': username})
            
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, self.template_name, {'username': username})
            
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, self.template_name, {'username': username})
            
        # Update password
        user.set_password(password1)
        user.save()
        update_session_auth_hash(request, user)  # Keep the user logged in if they are changing their own password
        messages.success(request, 'Your password has been reset successfully.')
        return redirect('login')
            
class ProfileView(LoginRequiredMixin,View):
    template_name = 'profiles/profile.html'

    def get(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        users_posts=Post.objects.filter(user=request.user,is_active=True).order_by('-created_at')
        pending_comments=Comment.objects.filter(post__user=request.user,is_approved=False).select_related('user','post')
        context={
            'profile': profile,
            'user_posts':users_posts,
            'pending_comments':pending_comments,
        }
        return render(request, self.template_name,context)
    
    def post(self, request):
        user=request.user
        profile, created = Profile.objects.get_or_create(user=user)
        
        email=request.POST.get('email')
        phone_number=request.POST.get('phone_number')
        country=request.POST.get('country')
        avatar=request.FILES.get('avatar')
        bio=request.POST.get('bio')
        
        # Update user and profile
        try:
            with transaction.atomic():
                user.email=email
                user.save()
                
                profile.phone_number=phone_number
                if country:
                    profile.country=country
                if avatar:
                    profile.avatar=avatar
                if bio:
                    profile.bio=bio
                profile.save()
                
                messages.success(request, 'Your profile has been updated successfully!')
        
        except Exception as e:
            messages.error(request, 'An error occurred. Please try again.')
            
        return redirect('profile')

@login_required
def approve_comment(request,pk):
    comment=get_object_or_404(Comment,pk=pk,post__user=request.user)
    comment.is_approved=True
    comment.save()
    messages.success(request, 'Comment has been approved and is now public.')
    return redirect('profile')