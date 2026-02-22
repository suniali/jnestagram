import uuid

from django.db import models
from django.conf import settings

class ChatGroup(models.Model):
    group_name = models.CharField(max_length=128,unique=True,default=uuid.uuid4)
    users_online=models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='online_in_groups',blank=True)
    members=models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='chat_groups',blank=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.group_name

class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup,on_delete=models.CASCADE,related_name='chat_messages')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-created_at']