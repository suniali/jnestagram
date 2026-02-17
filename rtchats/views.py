from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404,render
from django.urls import reverse_lazy

from .models import ChatGroup
from .forms import ChatMessageCreateForm

class ChatRoomView(LoginRequiredMixin,View):
    template_name = 'rtchats/chat_room.html'

    def prepare_context(self):
        chat_group = get_object_or_404(ChatGroup, group_name="jnestagram")
        chat_messages = chat_group.chat_messages.all()[:30]
        active_authors = chat_group.chat_messages.order_by('author').distinct('author')[:30]
        return {
            'chat_group':chat_group,
            'chat_messages':chat_messages,
            'active_authors':active_authors,
        }

    def get(self,request):
        context=self.prepare_context()
        form=ChatMessageCreateForm()
        context["form"]=form
        return render(request,self.template_name,context)

    def post(self, request):
        form=ChatMessageCreateForm(request.POST)
        chat_group=get_object_or_404(ChatGroup,group_name="jnestagram")

        if request.htmx and form.is_valid():
            chat_message=form.save(commit=False)
            chat_message.author=request.user
            chat_message.group=chat_group
            chat_message.save()

            context={
                'message':chat_message,
                'user':request.user
            }
            return render(request,'rtchats/chat_message.html',context)

        context=self.prepare_context()
        context["form"]=form
        return render(request,self.template_name,context)