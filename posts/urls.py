from django.urls import path

from .views import PostListView, like_post, PostCreateView, PostUpdateView, PostDeleteView

urlpatterns = [
    path('',PostListView.as_view(),name='home'),
    path('like/<int:post_id>/', like_post, name='like_post'),
    path('create/', PostCreateView.as_view(), name='create_post'),
    path('<int:pk>/update/',PostUpdateView.as_view(),name='update_post'),
    path('<int:pk>/delete/',PostDeleteView.as_view(),name='delete_post'),
]