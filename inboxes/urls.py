from django.urls import path

from .views import  ConversationListView

urlpatterns = [
    path('inbox/', ConversationListView.as_view(), name='inbox'),
]