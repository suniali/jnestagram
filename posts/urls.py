from django.urls import path

from .views import (PostListView, LikePostView, PostCreateView, PostUpdateView,
                    PostDeleteView, CommentCreateView, CommentUpdateView,
                    CommentDeleteView, PostDetailView,ReplayCreateView,ReplayDeleteView)

urlpatterns = [
    path('',PostListView.as_view(),name='home'),
    path('<pk>',PostDetailView.as_view(),name='post_detail'),
    path('<pk>/like/', LikePostView.as_view(), name='like_post'),
    path('create/', PostCreateView.as_view(), name='create_post'),
    path('<pk>/update/',PostUpdateView.as_view(),name='update_post'),
    path('<pk>/delete/',PostDeleteView.as_view(),name='delete_post'),
    path('<pk>/comment/', CommentCreateView.as_view(), name='add_comment'),
    path('comment/<pk>/edit/', CommentUpdateView.as_view(), name='update_comment'),
    path('comment/<pk>/delete/', CommentDeleteView.as_view(), name='delete_comment'),
    path('comment/<pk>/replay/', ReplayCreateView.as_view(), name='replay'),
    path('replay/<pk>/delete',ReplayDeleteView.as_view(), name='delete_replay'),
]