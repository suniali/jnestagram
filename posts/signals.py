from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F

from .models import Comment,Like,Replay

@receiver(post_save, sender=Like)
def update_like_count_on_save(sender, instance, created,**kwargs):
    obj=instance.content_object

    if created and obj and hasattr(obj,'likes_count'):
        obj.likes_count=F('likes_count')+1
        obj.save(update_fields=['likes_count'])

@receiver(post_delete, sender=Like)
def update_like_count_on_delete(sender, instance,**kwargs):
    obj=instance.content_object

    if obj and hasattr(obj,'likes_count'):
        if obj.likes_count > 0:
            obj.likes_count=F('likes_count')-1
            obj.save(update_fields=['likes_count'])
@receiver(post_save, sender=Comment)
def update_comments_count_on_save(sender, instance, created, **kwargs):
    if created:
        if instance.is_approved:
            instance.post.comments_count += 1
            instance.post.save(update_fields=['comments_count'])
    else:
        approved_count = instance.post.post_comments.filter(is_approved=True).count()
        if instance.post.comments_count != approved_count:
            instance.post.comments_count = approved_count
            instance.post.save(update_fields=['comments_count'])

@receiver(post_delete, sender=Comment)
def update_comments_count_on_delete(sender, instance, **kwargs):
    if instance.is_approved:
        approved_count = instance.post.post_comments.filter(is_approved=True).count()
        instance.post.comments_count = approved_count
        instance.post.save(update_fields=['comments_count'])

@receiver(post_save, sender=Replay)
def update_replay_count_on_save(sender, instance, created, **kwargs):
    comment=instance.comment
    if created and comment and hasattr(comment,'replays_count'):
        comment.replays_count += 1
        comment.save(update_fields=['replays_count'])
    else:
        replays_count=comment.comment_replays.count()
        if comment.replays_count!=replays_count:
            comment.replays_count=replays_count
            comment.save(update_fields=['replays_count'])

@receiver(post_delete, sender=Replay)
def update_replay_count_on_delete(sender, instance,**kwargs):
    comment=instance.comment
    if comment and hasattr(comment,'replays_count') and comment.replays_count > 0:
        comment.replays_count-=1
        comment.save(update_fields=['replays_count'])
