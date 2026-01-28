from .models import Comment

def pending_comments_count(request):
    if request.user.is_authenticated:
        count=Comment.objects.filter(post__user=request.user,is_approved=False).count()
        return  {'pending_comments_count':count}
    else:
        return {'pending_comments_count':0}