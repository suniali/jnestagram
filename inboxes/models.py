import uuid

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.timesince import timesince
from django.utils.translation import gettext_lazy as _

class Conversation(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4,unique=True, editable=False,verbose_name=_('ID'))
    participants=models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='conversations',verbose_name=_('Participants'))
    lastmessage_created=models.DateTimeField(default=timezone.now,verbose_name=_('Last Message Created'))
    is_seen = models.BooleanField(default=False,verbose_name=_('Is Seen'))

    class Meta:
        ordering = ['-lastmessage_created']

    def __str__(self):
        user_names=", ".join(user.username for user in self.participants.all())
        return f'[{user_names}]'

class Message(models.Model):
    sender=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='sent_message',verbose_name=_('Sender'))
    conversation=models.ForeignKey(Conversation,on_delete=models.CASCADE,related_name='messages',verbose_name=_('Conversation'))
    text = models.TextField(verbose_name=_('Text'))
    created_at=models.DateTimeField(auto_now_add=True,verbose_name=_('Created At'))

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        time_since=timesince(self.created_at,timezone.now())
        return f'[{self.sender.username} : {time_since} ago]'


