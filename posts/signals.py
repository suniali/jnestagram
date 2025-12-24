from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Post,Comment,Like

@receiver(post_save, sender=Like)
def update_like_count_on_save(sender, instance, created,**kwargs):
    if created:
        instance.post.likes_count+=1
        instance.post.save(update_fields=['likes_count'])

@receiver(post_delete, sender=Like)
def update_like_count_on_delete(sender, instance,**kwargs):
    if instance.post.likes_count >0:
        instance.post.likes_count-=1
        instance.post.save(update_fields=['likes_count'])

@receiver(post_save, sender=Comment)
def update_comments_count_on_save(sender, instance, created, **kwargs):
    if created:
        # اگر در لحظه ساخت تایید شده بود (مثلا توسط ادمین)
        if instance.is_approved:
            instance.post.comments_count += 1
            instance.post.save(update_fields=['comments_count'])
    else:
        # اگر کامنت از قبل وجود داشت و الان تایید شد (تغییر وضعیت)
        # ما چک می‌کنیم که آیا در این آپدیت، وضعیت تایید تغییر کرده یا نه
        # راه ساده‌تر: بازشماری کامنت‌های تایید شده همان پست
        approved_count = instance.post.comments.filter(is_approved=True).count()
        if instance.post.comments_count != approved_count:
            instance.post.comments_count = approved_count
            instance.post.save(update_fields=['comments_count'])

@receiver(post_delete, sender=Comment)
def update_comments_count_on_delete(sender, instance, **kwargs):
    # فقط اگر کامنت تایید شده بود و حذف شد، از تعداد کل کم کن
    if instance.is_approved:
        # برای اطمینان بیشتر، مجدد تعداد را دقیق حساب می‌کنیم
        approved_count = instance.post.comments.filter(is_approved=True).count()
        instance.post.comments_count = approved_count
        instance.post.save(update_fields=['comments_count'])