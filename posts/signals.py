from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Post,Comment,Like

@receiver(post_save, sender=Like)
def update_like_count_on_save(sender, instance, created,**kwargs):
    if created:
        instance.content_object.likes_count+=1
        instance.content_object.save(update_fields=['likes_count'])

@receiver(post_delete, sender=Like)
def update_like_count_on_delete(sender, instance,**kwargs):
    if instance.content_object.likes_count >0:
        instance.content_object.likes_count-=1
        instance.content_object.save(update_fields=['likes_count'])

@receiver(post_save, sender=Comment)
def update_comments_count_on_save(sender, instance, created, **kwargs):
    if created:
        if instance.is_approved:
            instance.post.comments_count += 1
            instance.post.save(update_fields=['comments_count'])
    else:
        approved_count = instance.post.comments.filter(is_approved=True).count()
        if instance.post.comments_count != approved_count:
            instance.post.comments_count = approved_count
            instance.post.save(update_fields=['comments_count'])

@receiver(post_delete, sender=Comment)
def update_comments_count_on_delete(sender, instance, **kwargs):
    if instance.is_approved:
        approved_count = instance.post.comments.filter(is_approved=True).count()
        instance.post.comments_count = approved_count
        instance.post.save(update_fields=['comments_count'])