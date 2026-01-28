import uuid

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.timesince import timesince

class Conversation(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4,unique=True, editable=False)
    participants=models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='conversations')
    lastmessage_created=models.DateTimeField(default=timezone.now)
    is_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ['-lastmessage_created']

    def __str__(self):
        user_names=", ".join(user.username for user in self.participants.all())
        return f'[{user_names}]'

class Message(models.Model):
    sender=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='sent_message')
    conversation=models.ForeignKey(Conversation,on_delete=models.CASCADE,related_name='messages')
    text = models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        time_since=timesince(self.created_at,timezone.now())
        return f'[{self.sender.username} : {time_since} ago]'


