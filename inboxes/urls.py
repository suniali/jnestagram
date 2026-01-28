from django.urls import path

from .views import ConversationListView, SearchUsersView, NewMessageView

urlpatterns = [
    path('inbox/', ConversationListView.as_view(), name='inbox'),
    path('search-users/', SearchUsersView.as_view(), name='inbox_search_users'),
    path('new-message/<int:recipient_id>', NewMessageView.as_view(), name='inbox_newmessage'),
]
