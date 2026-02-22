from django.http import Http404
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model

from .models import ChatGroup
from .forms import ChatMessageCreateForm

User=get_user_model()

class ChatRoomView(LoginRequiredMixin,View):
    template_name = 'rtchats/chat_room.html'

    def prepare_context(self,chatroom_name):
        chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
        other_user=None
        if chat_group.is_private:
            if self.request.user not in chat_group.members.all():
                raise Http404()
            other_user=chat_group.members.exclude(id=self.request.user.id).first()

        chat_messages = chat_group.chat_messages.all()[:30]
        active_authors = chat_group.chat_messages.order_by('author').distinct('author')[:30]
        return {
            'chat_group':chat_group,
            'chat_messages':chat_messages,
            'active_authors':active_authors,
            'other_user':other_user,
        }

    def get(self,request,chatroom_name='jnestagram'):
        context=self.prepare_context(chatroom_name)
        context["form"]=ChatMessageCreateForm()
        return render(request,self.template_name,context)

    def post(self, request,chatroom_name='jnestagram'):
        form=ChatMessageCreateForm(request.POST)
        context = self.prepare_context(chatroom_name)
        context["form"] = form

        if request.htmx and form.is_valid():
            chat_message=form.save(commit=False)
            chat_message.author=request.user
            chat_message.group=context['chat_group']
            chat_message.save()

            context={
                'message':chat_message,
                'user':request.user,
                'is_new':True,
            }
            return render(request,'rtchats/new_chat_message.html',context)

        return render(request,self.template_name,context)

class GetOrCreateChatRoomView(LoginRequiredMixin,View):
    def get(self, request,username):
        if not username or request.user.username==username:
            return redirect('chat_room')

        other_user=get_object_or_404(User,username=username)
        chatroom=ChatGroup.objects.filter(
            is_private=True,
            members=request.user,
        ).filter(members=other_user).first()

        if not chatroom:
            chatroom=ChatGroup.objects.create(is_private=True)
            chatroom.members.add(other_user,request.user)


        return redirect('private_chat_room',chatroom.group_name)
