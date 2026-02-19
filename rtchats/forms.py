from django import forms
from django.utils.translation import gettext_lazy as _

from .models import GroupMessage

class ChatMessageCreateForm(forms.ModelForm):
    class Meta:
        model=GroupMessage
        fields=('text',)
        widgets={
            'text':forms.TextInput(attrs={
                'placeholder':_('Add message ...'),
                'class':'flex-1 rd-full border-none outline-none py-2 px-2 text-sm font-600 text-slate-700 placeholder-slate-300 bg-transparent',
                'maxlength':300,
                'autofocus':True,
            }),
        }