from django.urls import path

from django.contrib.auth.views import (LogoutView,
                                       PasswordResetView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetCompleteView)

from .views import (CustomLoginView,RegisterView,ProfileView,PublicProfileView,
                    UserDeleteView,ComplateProfileView,approve_comment)

urlpatterns = [
    path('login/', CustomLoginView.as_view() ,name='login'),
    path('register/', RegisterView.as_view() ,name='register'),
    path('register/complate/',ComplateProfileView.as_view() ,name='complate_profile'),
    path('logout/', LogoutView.as_view() ,name='logout'),
    path('password-reset/', PasswordResetView.as_view(template_name='profiles/forgot_password.html'), name='password_reset'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='profiles/reset_password.html'), name='password_reset_confirm'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='profiles/password_reset_done.html'), name='password_reset_done'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='profiles/password_reset_complete.html'), name='password_reset_complete'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/',PublicProfileView.as_view(), name='public_profile'),
    path('profile/<pk>/delete/',UserDeleteView.as_view(), name='delete_profile'),
    path('comment/approve/<pk>/', approve_comment, name='approve_comment'),
]