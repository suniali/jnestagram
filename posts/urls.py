from django.urls import path

from .views import (PostListView, like_post, PostCreateView, PostUpdateView,
                    PostDeleteView,CommentCreateView,CommentUpdateView,CommentDeleteView)

urlpatterns = [
    path('',PostListView.as_view(),name='home'),
    path('like/<int:post_id>/', like_post, name='like_post'),
    path('create/', PostCreateView.as_view(), name='create_post'),
    path('<int:pk>/update/',PostUpdateView.as_view(),name='update_post'),
    path('<int:pk>/delete/',PostDeleteView.as_view(),name='delete_post'),
    path('<int:pk>/comment/', CommentCreateView.as_view(), name='add_comment'),
    path('comment/<int:pk>/edit/', CommentUpdateView.as_view(), name='update_comment'),
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='delete_comment'),
]