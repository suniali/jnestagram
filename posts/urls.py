from django.urls import path

from .views import (PostListView, LikeView, PostCreateView, PostUpdateView,
                    PostDeleteView, CommentCreateView, CommentUpdateView,
                    CommentDeleteView, PostDetailView,ReplayCreateView,ReplayDeleteView)

urlpatterns = [
    path('',PostListView.as_view(),name='home'),
    path('<pk>',PostDetailView.as_view(),name='post_detail'),
    path('like/<str:model_name>/<str:obj_id>/', LikeView.as_view(), name='like'),
    path('create/', PostCreateView.as_view(), name='create_post'),
    path('<pk>/update/',PostUpdateView.as_view(),name='update_post'),
    path('<pk>/delete/',PostDeleteView.as_view(),name='delete_post'),
    path('<pk>/comment/', CommentCreateView.as_view(), name='add_comment'),
    path('comment/<pk>/edit/', CommentUpdateView.as_view(), name='update_comment'),
    path('comment/<pk>/delete/', CommentDeleteView.as_view(), name='delete_comment'),
    path('comment/<pk>/replay/', ReplayCreateView.as_view(), name='replay'),
    path('replay/<pk>/delete',ReplayDeleteView.as_view(), name='delete_replay'),
]