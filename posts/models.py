import uuid

from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType

from django.db import models
from django.conf import settings
from django.urls import reverse

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

class Tag(models.Model):
    name = models.CharField(max_length=20,db_index=True)
    slug = models.SlugField(max_length=20,unique=True)
    icon= models.ImageField(upload_to='tags/%Y/%m/%d', null=True, blank=True)
    order=models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tags'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ('order',)
        
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('home')+'?tag='+self.slug


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=100)
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

    def __str__(self):
        return f"{self.user} liked {self.content_object}"

class Post(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_posts')
    title = models.CharField(max_length=100)
    image = ProcessedImageField(
        upload_to='posts/%Y/%m/%d',
        processors=[ResizeToFill(1080, 566)],
        format='WEBP',
        options={'quality': 80}
    )
    text = models.TextField()
    tag= models.ManyToManyField(Tag, related_name='tag_posts',blank=True)
    likes=GenericRelation(Like,related_query_name='posts')
    likes_count=models.PositiveIntegerField(default=0)
    comments_count=models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'posts'
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        indexes=[
            models.Index(fields=['-likes_count','-created_at']),
            models.Index(fields=['is_active','is_public','-created_at']),
            models.Index(fields=['user','-created_at']),
        ]
        
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='user_comments')
    text = models.TextField()
    likes=GenericRelation(Like,related_query_name='comments')
    likes_count=models.PositiveIntegerField(default=0)
    replays_count=models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'comments'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        indexes=[
            models.Index(fields=['-likes_count','-created_at']),
            models.Index(fields=['post','is_approved','-created_at']),
            models.Index(fields=['user','-created_at']),
        ]

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.title}'

class Replay(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_replays')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_replays')
    text = models.TextField()
    likes=GenericRelation(Like,related_query_name='replays')
    likes_count=models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'replays'
        verbose_name = 'Replay'
        verbose_name_plural = 'Replays'
        indexes=[
            models.Index(fields=['-likes_count','-created_at']),
            models.Index(fields=['comment','-created_at']),
            models.Index(fields=['user','-created_at']),
        ]

    def __str__(self):
        return  self.text
