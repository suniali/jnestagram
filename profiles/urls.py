from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (CustomLoginView,RegisterView,
                    LogoutView,ForgotPasswordView,
                    ResetPasswordView,ProfileView,PublicProfileView,
                    UserDeleteView,ComplateProfileView,approve_comment)

urlpatterns = [
    path('login/', CustomLoginView.as_view() ,name='login'),
    path('register/', RegisterView.as_view() ,name='register'),
    path('register/complate/',ComplateProfileView.as_view() ,name='complate_profile'),
    path('logout/', LogoutView.as_view() ,name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<str:username>/', ResetPasswordView.as_view(), name='reset_password'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/',PublicProfileView.as_view(), name='public_profile'),
    path('profile/<pk>/delete/',UserDeleteView.as_view(), name='delete_profile'),
    path('comment/approve/<pk>/', approve_comment, name='approve_comment'),
]