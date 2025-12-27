from django import forms

from .models import Post, Comment, Replay, Like


class PostForm(forms.ModelForm):
    class Meta:
        model=Post
        fields=['title','text','image','is_public']

class CommentForm(forms.ModelForm):
    class Meta:
        model=Comment
        fields=['text']

class ReplayForm(forms.ModelForm):
    class Meta:
        model=Replay
        fields=['text']

