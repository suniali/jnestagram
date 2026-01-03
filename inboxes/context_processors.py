from .models import Conversation

def inbox_messages_count(request):
    if request.user.is_authenticated:
        unread_conversations=Conversation.objects.filter(
            participants=request.user,
            is_seen=False
        ).prefetch_related('messages')

        unread_messages_count=0
        for conversation in unread_conversations:
            all_messages=conversation.messages.all()
            if all_messages.exists():
                last_message=all_messages.last()
                if last_message.sender != request.user:
                    unread_messages_count+=1

        return {'unread_messages_count':unread_messages_count}
    else:
        return {'unread_messages_count':0}