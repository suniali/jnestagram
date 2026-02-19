from django.urls import path

from .views import *

urlpatterns = [
    path('chats/',ChatRoomView.as_view(), name='chat_room'),
]