from django.urls import path

from .views import (PostListView, like_post, PostCreateView, PostUpdateView,
                    PostDeleteView, CommentCreateView, CommentUpdateView, CommentDeleteView, PostDetailView)

urlpatterns = [
    path('',PostListView.as_view(),name='home'),
    path('<pk>',PostDetailView.as_view(),name='post_detail'),
    path('like/<post_id>/', like_post, name='like_post'),
    path('create/', PostCreateView.as_view(), name='create_post'),
    path('<pk>/update/',PostUpdateView.as_view(),name='update_post'),
    path('<pk>/delete/',PostDeleteView.as_view(),name='delete_post'),
    path('<pk>/comment/', CommentCreateView.as_view(), name='add_comment'),
    path('comment/<pk>/edit/', CommentUpdateView.as_view(), name='update_comment'),
    path('comment/<pk>/delete/', CommentDeleteView.as_view(), name='delete_comment'),
]