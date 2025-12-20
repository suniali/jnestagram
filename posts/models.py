from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='posts/%Y/%m/%d')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
