from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, Http404
from django.db.models import Q

from .models import Conversation, Message

User = get_user_model()


class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'inboxes/inbox.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants').order_by('-lastmessage_created')

    def get(self, request, *args, **kwargs):
        if self.request.htmx:
            conversation_id = self.request.GET.get('pk')
            if conversation_id:
                conversation = get_object_or_404(Conversation, pk=conversation_id, participants=request.user)
                conversation.other_user = conversation.participants.exclude(id=request.user.id).first()

                messages = Message.objects.filter(conversation=conversation).select_related('sender').order_by(
                    'created_at')

                conversations = Conversation.objects.filter(participants=request.user).prefetch_related(
                    'participants').order_by('-lastmessage_created')
                for conv in conversations:
                    conv.other_user = conv.participants.exclude(id=request.user.id).first()

                return render(self.request, 'inboxes/conversation.html', {
                    'conversations': conversations,
                    'conversation': conversation,
                    'messages': messages,
                })

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        active_pk = self.request.GET.get('pk')

        conversations = list(context['conversations'])

        for conv in conversations:
            all_participants = conv.participants.all()
            conv.other_user = next((u for u in all_participants if u.id != self.request.user), None)

            if active_pk and str(conv.id) == active_pk:
                context['conversation'] = conv
                context['messages'] = Message.objects.filter(conversation=conv).select_related('sender').order_by(
                    'created_at')

        context['conversations'] = conversations
        return context


class SearchUsersView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'inboxes/partials/users_list.html'

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
    template_name = 'inboxes/partials/form_newmessage.html'

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
                Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    text=message_text,
                )

                messages = conversation.messages.all().order_by('created_at')
                return render(request, 'inboxes/conversation.html',
                              {'messages': messages, 'conversation': conversation})

        else:
            raise Http404('ID Not Found!')
