from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (LoginView,RegisterView,
                    LogoutView,ForgotPasswordView,
                    ResetPasswordView,ProfileView)

urlpatterns = [
    path('login/', LoginView.as_view() ,name='login'),
    path('register/', RegisterView.as_view() ,name='register'),
    path('logout/', LogoutView.as_view() ,name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<str:username>/', ResetPasswordView.as_view(), name='reset_password'),
    path('profile/', ProfileView.as_view(), name='profile'),
]