from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from .models import ChatGroup
from .forms import ChatMessageCreateForm

class ChatRoomView(LoginRequiredMixin,CreateView):
    template_name = 'rtchats/chatroom.html'
    form_class = ChatMessageCreateForm
    success_url = reverse_lazy("chat_room")

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        chat_group=get_object_or_404(ChatGroup,group_name="jnestagram")
        context['chat_group']=chat_group
        context['chat_messages']=chat_group.chat_messages.all()[:30]
        context['active_authors']=chat_group.chat_messages.order_by('author').distinct('author')[:30]
        return context

    def form_valid(self, form):
        chat_group=get_object_or_404(ChatGroup,group_name="jnestagram")

        form.instance.author=self.request.user
        form.instance.group=chat_group

        return super().form_valid(form)

