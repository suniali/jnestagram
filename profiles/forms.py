from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from profiles.models import Profile

User=get_user_model()

class RegistrationForm(UserCreationForm):
    email=forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username', 'email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'input-main'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered!')
        return email

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'avatar','country', 'phone_number')
        extra_kwargs = {
            'bio': {'required': False},
            'avatar': {'required': False},
            'country': {'required': False},
            'phone_number': {'required': False},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input-main'})

            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': 'input-main h-32 resize-none',
                    'placeholder':'Write about yourself ...'
                })
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    'class': 'input-main appearance-none bg-no-repeat bg-right-4'
                })
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if Profile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('Phone number already registered!')
        return phone_number