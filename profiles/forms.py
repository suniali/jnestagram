from django import forms

from profiles.models import Profile


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