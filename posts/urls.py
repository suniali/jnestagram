from django.urls import path

from .views import PostListView,like_post,PostCreateView

urlpatterns = [
    path('',PostListView.as_view(),name='home'),
    path('like/<int:post_id>/', like_post, name='like_post'),
    path('create/', PostCreateView.as_view(), name='create_post'),
]