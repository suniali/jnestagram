from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, Http404
from django.db.models import Q
from django.utils import timezone
from cryptography.fernet import Fernet

from .models import Conversation, Message
from jnestagram.settings import env

User = get_user_model()
f=Fernet(env('ENCRYPT_KEY'))


class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'inboxes/inbox.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants').order_by('-lastmessage_created')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        active_pk = self.request.GET.get('pk')

        conversations = list(context['conversations'])

        for conv in conversations:
            all_participants = conv.participants.all()
            conv.other_user = next((u for u in all_participants if u.id != self.request.user.id), None)

            if active_pk and str(conv.id) == active_pk:
                if conv.is_seen == False and conv.messages.last().sender != self.request.user:
                    conv.is_seen = True
                    conv.save()

                # Decrypting
                inbox_messages=Message.objects.filter(conversation=conv).select_related('sender').order_by(
                    'created_at')


                context['conversation'] = conv
                context['inbox_messages'] = inbox_messages

        context['conversations'] = conversations
        return context

class ChatsListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'inboxes/chats.html'

    def get_queryset(self):
        return Message.objects.filter(
            conversation=self.kwargs['pk']
        ).select_related('sender').order_by('created_at')

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        request=self.request
        conversation_id = self.kwargs.get('pk')

        if conversation_id:
            conversation = get_object_or_404(Conversation, pk=conversation_id, participants=request.user)
            conversation.other_user = conversation.participants.exclude(id=request.user.id).first()


            if not conversation.is_seen and conversation.messages.exists():
                last_msg = conversation.messages.last()
                if last_msg.sender != request.user:
                    conversation.is_seen = True
                    conversation.save()

            context['conversation'] = conversation
            context['chats'] = self.get_queryset()

        return context

class SearchUsersView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'partials/inboxes/users_list.html'

    def get(self, request, *args, **kwargs):
        letters = request.GET.get('search_user')
        if request.htmx:
            if len(letters) > 0:
                users = User.objects.filter(
                    Q(username__icontains=letters) |
                    Q(first_name__icontains=letters) |
                    Q(last_name__icontains=letters)
                ).exclude(username=request.user.username)
                return render(request, self.template_name, {'users': users})
            else:
                return HttpResponse('')
        else:
            raise Http404()


class NewMessageView(LoginRequiredMixin, View):
    template_name = 'partials/inboxes/form_newmessage.html'

    def get(self, request, recipient_id):
        if recipient_id:
            recipient = get_object_or_404(User, pk=recipient_id)
            context = {'recipient': recipient}
            return render(request, self.template_name, context)
        else:
            raise Http404('ID Not Found!')

    def post(self, request, recipient_id):
        if recipient_id:
            recipient = get_object_or_404(User, pk=recipient_id)
            message_text = request.POST.get('message')

            if message_text:
                conversation = Conversation.objects.filter(participants=request.user).filter(
                    participants=recipient).first()
                if not conversation:
                    conversation = Conversation.objects.create()
                    conversation.participants.add(request.user, recipient)

                conversation.other_user = conversation.participants.exclude(id=request.user.id).first()

                # Encrypting
                message_encrypted = f.encrypt(message_text.encode('utf-8')).decode('utf-8')

                Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    text=message_encrypted,
                )

                conversation.lastmessage_created = timezone.now()
                conversation.is_seen=False
                conversation.save()

                inbox_messages = conversation.messages.all().order_by('created_at')
                context={
                    'chats': inbox_messages,
                    'conversation': conversation,
                }

                if self.request.htmx:
                    return render(request, 'inboxes/message_list.html', context)

                return redirect(f'/chats/{conversation.pk}/',context)
