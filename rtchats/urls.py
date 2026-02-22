from django.urls import path

from .views import *

urlpatterns = [
    path('chats/',ChatRoomView.as_view(), name='chat_room'),
    path('chats/<username>/',GetOrCreateChatRoomView.as_view(), name='start_chat'),
    path('chats/room/<str:chatroom_name>/',ChatRoomView.as_view(), name='private_chat_room'),
]