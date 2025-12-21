from django.urls import path

from .views import PostListView,like_post

urlpatterns = [
    path('',PostListView.as_view(),name='home'),
    path('like/<int:post_id>/', like_post, name='like_post'),
]