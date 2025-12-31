from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Conversation,Message

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

                messages = Message.objects.filter(conversation=conversation).select_related('sender').order_by('created_at')

                conversations=Conversation.objects.filter(participants=request.user).prefetch_related('participants').order_by('-lastmessage_created')
                for conv in conversations:
                    conv.other_user = conv.participants.exclude(id=request.user.id).first()

                return render(self.request, 'inboxes/conversation.html', {
                    'conversations':conversations,
                    'conversation': conversation,
                    'messages': messages,
                })

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)

        active_pk=self.request.GET.get('pk')

        conversations=list(context['conversations'])

        for conv in conversations:
            all_participants=conv.participants.all()
            conv.other_user=next((u for u in all_participants if u.id != self.request.user), None)

            if active_pk and str(conv.id) == active_pk:
                context['conversation'] = conv
                context['messages'] = Message.objects.filter(conversation=conv).select_related('sender').order_by(
                    'created_at')

        context['conversations']=conversations
        return context